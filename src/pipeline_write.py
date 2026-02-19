from __future__ import annotations

import argparse
import json
from pathlib import Path

from datetime import datetime, timedelta, timezone
from jsonschema import validate

from .audit_log import append_audit
from .config import ROOT, load_config
from .embedder import get_embedding
from .extractor import extract_candidates
from .fallback_store import write_fallback
from .normalizer import normalize_candidates
from .store_qdrant import deterministic_point_id, health_check, upsert_points
from .validator import validate_memories



def _load_schema(name: str) -> dict:
    p = ROOT / "schemas" / name
    return json.loads(p.read_text(encoding="utf-8"))



def run_write(text: str, user_id: str, session_id: str, message_id: str) -> dict:
    cfg = load_config()

    if not cfg.enable_write:
        append_audit("write.disabled", {"user_id": user_id, "reason": "MEMORY_ENABLE_WRITE=false"})
        return {"stored": 0, "rejected": 0, "items": [], "disabled": True}

    if not str(user_id).strip() or text is None:
        raise ValueError("user_id/text is required")

    extracted = extract_candidates(text)
    validate(instance=extracted, schema=_load_schema("extract.output.schema.json"))

    normalized = normalize_candidates(extracted)
    validate(instance=normalized, schema=_load_schema("normalize.output.schema.json"))

    validated = validate_memories(normalized, min_confidence=cfg.min_confidence)
    validate(instance=validated, schema=_load_schema("validate.output.schema.json"))

    if not validated["accepted"]:
        append_audit("write.noop", {"user_id": user_id, "reason": "no_accepted", "rejected": len(validated["rejected"])})
        return {"stored": 0, "rejected": len(validated["rejected"]), "items": []}

    now = datetime.now(timezone.utc)
    payload_items = []
    points = []
    for item in validated["accepted"]:
        exp = None
        if item.get("ttl_days"):
            exp = (now + timedelta(days=int(item["ttl_days"]))).isoformat()
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "message_id": message_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "expires_at": exp,
            **item,
        }
        payload_items.append(payload)
        points.append(
            {
                "id": deterministic_point_id(user_id, str(item["canonical_key"]), str(item["value"])),
                "vector": get_embedding(item["value"]),
                "payload": payload,
            }
        )

    if not health_check(cfg.qdrant_url):
        write_fallback(payload_items)
        append_audit("write.fallback", {"user_id": user_id, "count": len(payload_items), "reason": "qdrant_unhealthy"})
        return {
            "stored": len(payload_items),
            "rejected": len(validated["rejected"]),
            "items": validated["accepted"],
            "fallback": True,
        }

    try:
        upsert_resp = upsert_points(
            qdrant_url=cfg.qdrant_url,
            collection=cfg.qdrant_collection,
            points=points,
            api_key=cfg.qdrant_api_key,
        )
        append_audit("write.qdrant", {"user_id": user_id, "stored": len(points), "rejected": len(validated["rejected"])})

        return {
            "stored": len(validated["accepted"]),
            "rejected": len(validated["rejected"]),
            "items": validated["accepted"],
            "upsert": upsert_resp,
            "fallback": False,
        }
    except Exception as e:
        write_fallback(payload_items)
        append_audit(
            "write.fallback",
            {
                "user_id": user_id,
                "count": len(payload_items),
                "reason": "qdrant_upsert_error",
                "error": str(e),
            },
        )
        return {
            "stored": len(payload_items),
            "rejected": len(validated["rejected"]),
            "items": validated["accepted"],
            "fallback": True,
            "error": "qdrant_upsert_error",
        }



def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 2 write pipeline")
    ap.add_argument("--input", type=str, required=True, help="Path to json input")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = run_write(
        text=data["text"],
        user_id=str(data["user_id"]),
        session_id=str(data.get("session_id", "main")),
        message_id=str(data.get("message_id", "manual")),
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "logs" / "memory_audit.jsonl"


ALLOWED_PAYLOAD_KEYS = {
    "user_id",
    "query",
    "results",
    "fallback",
    "reason",
    "count",
    "stored",
    "rejected",
    "canonical_key",
    "fallback_removed",
    "error",
}



def _sanitize(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in payload.items():
        if k in ALLOWED_PAYLOAD_KEYS:
            out[k] = v
    return out



def append_audit(event: str, payload: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": _sanitize(payload),
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

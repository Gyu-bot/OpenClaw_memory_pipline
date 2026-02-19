from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]



def _load_policy() -> dict[str, Any]:
    with (ROOT / "policy" / "memory_policy.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)



def _load_sensitive_patterns() -> list[dict[str, str]]:
    with (ROOT / "policy" / "sensitive_patterns.yaml").open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("patterns", [])



def validate_memories(normalized_out: dict[str, list[dict[str, Any]]], min_confidence: float | None = None) -> dict[str, list[dict[str, Any]]]:
    policy = _load_policy()
    patterns = _load_sensitive_patterns()

    allowed = set(policy.get("allowed_types", []))
    ttl_days = policy.get("ttl_days", {})
    threshold = float(min_confidence if min_confidence is not None else policy.get("min_confidence", 0.75))

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for item in normalized_out.get("normalized", []):
        ctype = item.get("type")
        value = str(item.get("value", ""))
        conf = float(item.get("confidence", 0.0))

        if ctype not in allowed:
            rejected.append({"reason": "type_not_allowed", "item": item})
            continue

        if conf < threshold:
            rejected.append({"reason": "low_confidence", "item": item})
            continue

        sensitive_hit = None
        for p in patterns:
            if re.search(p["regex"], value):
                sensitive_hit = p["name"]
                break

        if sensitive_hit:
            rejected.append({"reason": f"sensitive:{sensitive_hit}", "item": item})
            continue

        accepted.append(
            {
                "type": ctype,
                "canonical_key": item.get("canonical_key"),
                "value": value,
                "confidence": conf,
                "ttl_days": ttl_days.get(ctype),
            }
        )

    return {"accepted": accepted, "rejected": rejected}

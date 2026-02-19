from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ALLOWED_TYPES = {"preference", "profile", "project_state", "task_rule", "do_not_store"}
ROOT = Path(__file__).resolve().parents[1]


def _load_policy() -> dict[str, Any]:
    with (ROOT / "policy" / "extractor_policy.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _contains_trigger(text: str, items: list[str]) -> bool:
    t = text.lower()
    for k in items:
        if k.isascii():
            if k.lower() in t:
                return True
        else:
            if k in text:
                return True
    return False


def _extract_memory_target(text: str, positive_triggers: list[str]) -> str:
    t = text.strip()

    trig_pattern = "|".join(re.escape(x) for x in sorted(positive_triggers, key=len, reverse=True))
    m = re.search(rf"(?:{trig_pattern})\s*[:：\-]\s*(.+)$", t, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    t2 = re.sub(rf"\s*(?:{trig_pattern})\s*$", "", t, flags=re.IGNORECASE).strip()
    return t2 if t2 else t


def _is_meaningful(text: str, min_compact_length: int, insufficient_values: set[str]) -> bool:
    s = re.sub(r"\s+", "", text)
    if len(s) < int(min_compact_length):
        return False
    if s in insufficient_values:
        return False
    return True


def extract_candidates(text: str) -> dict[str, list[dict[str, Any]]]:
    policy = _load_policy()

    positive = policy.get("positive_triggers", [])
    negative = policy.get("negative_triggers", [])
    sensitive_hints = policy.get("sensitive_hints", [])
    insufficient_values = set(policy.get("insufficient_values", []))
    min_compact_length = int(policy.get("min_compact_length", 6))
    max_value_length = int(policy.get("max_value_length", 500))
    default_type = str(policy.get("default_type", "task_rule"))
    default_key = str(policy.get("default_key", "explicit_memory_note"))
    default_confidence = float(policy.get("default_confidence", 0.95))

    t = (text or "").strip()
    if not t:
        return {"candidates": []}

    lowered = t.lower()
    candidates: list[dict[str, Any]] = []

    if any(k.lower() in lowered for k in sensitive_hints):
        candidates.append(
            {
                "type": "do_not_store",
                "key": "sensitive_hint",
                "value": "민감정보 포함 가능성",
                "confidence": 1.0,
                "evidence": t,
            }
        )

    if _contains_trigger(t, negative):
        return {"candidates": candidates}

    if not _contains_trigger(t, positive):
        return {"candidates": candidates}

    value = _extract_memory_target(t, positive)

    if not _is_meaningful(value, min_compact_length=min_compact_length, insufficient_values=insufficient_values):
        candidates.append(
            {
                "type": "do_not_store",
                "key": "insufficient_content",
                "value": "기억 대상 정보량 부족",
                "confidence": 1.0,
                "evidence": t,
            }
        )
        return {"candidates": candidates}

    candidates.append(
        {
            "type": default_type,
            "key": default_key,
            "value": value[:max_value_length],
            "confidence": default_confidence,
            "evidence": t,
        }
    )

    for c in candidates:
        if c["type"] not in ALLOWED_TYPES:
            c["type"] = "do_not_store"

    return {"candidates": candidates}

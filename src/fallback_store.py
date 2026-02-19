from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FALLBACK_PATH = ROOT / "data" / "fallback_memories.jsonl"


def _parse_ts(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def write_fallback(items: list[dict[str, Any]]) -> None:
    FALLBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FALLBACK_PATH.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def read_fallback(user_id: str, limit: int = 10) -> list[dict[str, Any]]:
    if not FALLBACK_PATH.exists():
        return []
    out = []
    now = datetime.now(timezone.utc)
    with FALLBACK_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if str(row.get("user_id")) != str(user_id):
                continue

            exp = _parse_ts(row.get("expires_at"))
            if exp and exp < now:
                continue

            out.append(row)
    return out[-limit:]


def delete_fallback_by_key(user_id: str, canonical_key: str) -> int:
    if not FALLBACK_PATH.exists():
        return 0
    kept = []
    removed = 0
    with FALLBACK_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                removed += 1
                continue
            if str(row.get("user_id")) == str(user_id) and str(row.get("canonical_key")) == str(canonical_key):
                removed += 1
                continue
            kept.append(row)

    with FALLBACK_PATH.open("w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return removed


def delete_fallback_by_user(user_id: str) -> int:
    if not FALLBACK_PATH.exists():
        return 0
    kept = []
    removed = 0
    with FALLBACK_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                removed += 1
                continue
            if str(row.get("user_id")) == str(user_id):
                removed += 1
                continue
            kept.append(row)

    with FALLBACK_PATH.open("w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return removed

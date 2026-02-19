from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FALLBACK_PATH = ROOT / "data" / "fallback_memories.jsonl"


def _parse_ts(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def cleanup_fallback_expired() -> int:
    if not FALLBACK_PATH.exists():
        return 0

    now = datetime.now(timezone.utc)
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

            exp = _parse_ts(row.get("expires_at"))
            if exp and exp < now:
                removed += 1
                continue
            kept.append(row)

    with FALLBACK_PATH.open("w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return removed

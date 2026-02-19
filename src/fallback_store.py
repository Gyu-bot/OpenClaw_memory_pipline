from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FALLBACK_PATH = ROOT / "data" / "fallback_memories.jsonl"


def write_fallback(items: list[dict[str, Any]]) -> None:
    FALLBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FALLBACK_PATH.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def read_fallback(user_id: str, limit: int = 10) -> list[dict[str, Any]]:
    if not FALLBACK_PATH.exists():
        return []
    out = []
    with FALLBACK_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if str(row.get("user_id")) == str(user_id):
                out.append(row)
    return out[-limit:]

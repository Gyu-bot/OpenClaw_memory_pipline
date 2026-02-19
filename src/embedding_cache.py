from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "data" / "embedding_cache.json"


def _load_all() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_all(data: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def cache_get(key: str) -> list[float] | None:
    data = _load_all()
    vec = data.get(key)
    if isinstance(vec, list):
        return vec
    return None


def cache_set(key: str, vector: list[float]) -> None:
    data = _load_all()
    data[key] = vector
    _save_all(data)

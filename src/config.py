from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class AppConfig:
    qdrant_url: str
    qdrant_collection: str
    qdrant_api_key: str | None
    min_confidence: float
    ttl_days: dict[str, int | None]
    top_k: int
    max_inject_tokens: int
    enable_write: bool
    enable_read: bool
    recency_half_life_days: int



def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)



def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}



def load_config() -> AppConfig:
    policy = load_yaml(ROOT / "policy" / "memory_policy.yaml")
    return AppConfig(
        qdrant_url=os.getenv("QDRANT_URL", "http://127.0.0.1:6333"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "agent_memory"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        min_confidence=float(os.getenv("MEMORY_MIN_CONFIDENCE", policy.get("min_confidence", 0.75))),
        ttl_days=policy.get("ttl_days", {}),
        top_k=int(os.getenv("MEMORY_TOP_K", policy.get("top_k", 6))),
        max_inject_tokens=int(os.getenv("MEMORY_MAX_INJECT_TOKENS", policy.get("max_inject_tokens", 1200))),
        enable_write=_bool_env("MEMORY_ENABLE_WRITE", True),
        enable_read=_bool_env("MEMORY_ENABLE_READ", True),
        recency_half_life_days=int(os.getenv("MEMORY_RECENCY_HALF_LIFE_DAYS", "14")),
    )

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from typing import List

from .embedding_cache import cache_get, cache_set



def fake_embedding(text: str, dim: int = 1536) -> List[float]:
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    vals = []
    for i in range(dim):
        b = seed[i % len(seed)]
        vals.append((b / 255.0) - 0.5)
    return vals



def _cache_key(model: str, text: str) -> str:
    return hashlib.sha256(f"{model}::{text}".encode("utf-8")).hexdigest()



def get_embedding(text: str) -> List[float]:
    model = os.getenv("MEMORY_EMBEDDING_MODEL", "text-embedding-3-small")
    key = _cache_key(model, text)

    cached = cache_get(key)
    if cached is not None:
        return cached

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        vec = fake_embedding(text)
        cache_set(key, vec)
        return vec

    payload = {"model": model, "input": text}
    req = urllib.request.Request(
        url="https://api.openai.com/v1/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    vec = body["data"][0]["embedding"]
    cache_set(key, vec)
    return vec

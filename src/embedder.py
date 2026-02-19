from __future__ import annotations

import hashlib
from typing import List



def fake_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    PoC용 deterministic embedding.
    실제 운영에서는 OpenAI embedding 호출로 교체.
    """
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    vals = []
    for i in range(dim):
        b = seed[i % len(seed)]
        vals.append((b / 255.0) - 0.5)
    return vals

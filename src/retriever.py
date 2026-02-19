from __future__ import annotations

import json
import urllib.request
from typing import Any

from .embedder import get_embedding



def _request(method: str, url: str, payload: dict[str, Any] | None = None, api_key: str | None = None) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))



def retrieve_memories(
    qdrant_url: str,
    collection: str,
    query: str,
    user_id: str,
    limit: int = 10,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    vector = get_embedding(query)
    payload = {
        "vector": vector,
        "limit": limit,
        "with_payload": True,
        "with_vector": False,
        "filter": {
            "must": [
                {
                    "key": "user_id",
                    "match": {"value": user_id},
                }
            ]
        },
    }

    url = f"{qdrant_url.rstrip('/')}/collections/{collection}/points/search"
    resp = _request("POST", url, payload, api_key)
    return resp.get("result", [])

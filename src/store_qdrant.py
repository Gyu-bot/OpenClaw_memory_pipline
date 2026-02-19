from __future__ import annotations

import hashlib
import json
import urllib.request
from typing import Any



def _request(method: str, url: str, payload: dict[str, Any] | None = None, api_key: str | None = None) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)



def upsert_points(qdrant_url: str, collection: str, points: list[dict[str, Any]], api_key: str | None = None) -> dict[str, Any]:
    url = f"{qdrant_url.rstrip('/')}/collections/{collection}/points"
    return _request("PUT", url, {"points": points}, api_key)



def delete_points_by_filter(qdrant_url: str, collection: str, qfilter: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
    url = f"{qdrant_url.rstrip('/')}/collections/{collection}/points/delete"
    return _request("POST", url, {"filter": qfilter}, api_key)



def health_check(qdrant_url: str) -> bool:
    try:
        url = f"{qdrant_url.rstrip('/')}/healthz"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return b"healthz check passed" in resp.read()
    except Exception:
        return False



def deterministic_point_id(user_id: str, canonical_key: str, value: str) -> str:
    raw = f"{user_id}|{canonical_key}|{value}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]

from __future__ import annotations

import argparse
import json

from .audit_log import append_audit
from .config import load_config
from .store_qdrant import delete_points_by_filter



def forget_by_key(user_id: str, canonical_key: str) -> dict:
    cfg = load_config()
    qfilter = {
        "must": [
            {"key": "user_id", "match": {"value": user_id}},
            {"key": "canonical_key", "match": {"value": canonical_key}},
        ]
    }
    resp = delete_points_by_filter(cfg.qdrant_url, cfg.qdrant_collection, qfilter, cfg.qdrant_api_key)
    append_audit("forget.key", {"user_id": user_id, "canonical_key": canonical_key, "resp": resp})
    return resp



def forget_all_user(user_id: str) -> dict:
    cfg = load_config()
    qfilter = {"must": [{"key": "user_id", "match": {"value": user_id}}]}
    resp = delete_points_by_filter(cfg.qdrant_url, cfg.qdrant_collection, qfilter, cfg.qdrant_api_key)
    append_audit("forget.user", {"user_id": user_id, "resp": resp})
    return resp



def main() -> None:
    ap = argparse.ArgumentParser(description="Forget handler")
    ap.add_argument("--user-id", required=True)
    ap.add_argument("--canonical-key", default=None)
    args = ap.parse_args()

    if args.canonical_key:
        out = forget_by_key(args.user_id, args.canonical_key)
    else:
        out = forget_all_user(args.user_id)

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

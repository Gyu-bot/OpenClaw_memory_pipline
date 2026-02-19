from __future__ import annotations

import argparse
import json
from typing import Any

from .audit_log import append_audit
from .config import load_config
from .fallback_store import read_fallback
from .reranker import rerank_results
from .retriever import retrieve_memories



def _truncate_memories(memories: list[str], max_chars: int) -> list[str]:
    out: list[str] = []
    total = 0
    for m in memories:
        if total + len(m) > max_chars:
            break
        out.append(m)
        total += len(m)
    return out



def run_read(query: str, user_id: str) -> dict[str, Any]:
    cfg = load_config()

    fallback_used = False
    try:
        raw = retrieve_memories(
            qdrant_url=cfg.qdrant_url,
            collection=cfg.qdrant_collection,
            query=query,
            user_id=user_id,
            limit=20,
            api_key=cfg.qdrant_api_key,
        )
    except Exception:
        fallback_used = True
        rows = read_fallback(user_id=user_id, limit=20)
        raw = [
            {
                "id": r.get("message_id", "fallback"),
                "score": 0.0,
                "payload": r,
            }
            for r in rows
        ]

    ranked = rerank_results(raw)
    top_k = ranked[:6]

    memories = []
    for r in top_k:
        p = r.get("payload", {})
        if p.get("value"):
            memories.append(str(p["value"]))

    # PoC: token budget 대신 문자 예산으로 단순 제한
    bounded = _truncate_memories(memories, max_chars=1200)

    append_audit("read.query", {"user_id": user_id, "query": query, "results": len(top_k), "fallback": fallback_used})

    return {
        "query": query,
        "count": len(bounded),
        "memories": bounded,
        "fallback": fallback_used,
        "debug": [
            {
                "id": r.get("id"),
                "score": r.get("score"),
                "final_score": r.get("final_score"),
                "payload": r.get("payload", {}),
            }
            for r in top_k
        ],
    }



def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 3 read pipeline")
    ap.add_argument("--query", required=True)
    ap.add_argument("--user-id", required=True)
    args = ap.parse_args()

    out = run_read(args.query, args.user_id)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

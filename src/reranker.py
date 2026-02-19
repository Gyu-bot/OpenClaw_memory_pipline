from __future__ import annotations

from typing import Any



def rerank_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    PoC reranker:
    - relevance(score) + confidence(payload)
    - recency는 추후 created_at 기준으로 추가 예정
    """
    ranked = []
    for r in results:
        payload = r.get("payload", {})
        relevance = float(r.get("score", 0.0))
        confidence = float(payload.get("confidence", 0.0))
        final = (0.8 * relevance) + (0.2 * confidence)
        item = dict(r)
        item["final_score"] = final
        ranked.append(item)

    ranked.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
    return ranked

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any



def _parse_ts(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None



def _recency_score(payload: dict[str, Any], half_life_days: int = 14) -> float:
    ts = _parse_ts(payload.get("updated_at") or payload.get("created_at"))
    if ts is None:
        return 0.3  # timestamp 없으면 중립보다 약간 낮게

    now = datetime.now(timezone.utc)
    age_days = max((now - ts).total_seconds() / 86400.0, 0.0)
    lam = math.log(2) / max(float(half_life_days), 1.0)
    return float(math.exp(-lam * age_days))



def rerank_results(results: list[dict[str, Any]], half_life_days: int = 14) -> list[dict[str, Any]]:
    """
    final = 0.65*relevance + 0.20*confidence + 0.15*recency
    """
    ranked = []
    for r in results:
        payload = r.get("payload", {})
        relevance = float(r.get("score", 0.0))
        confidence = float(payload.get("confidence", 0.0))
        recency = _recency_score(payload, half_life_days=half_life_days)
        final = (0.65 * relevance) + (0.20 * confidence) + (0.15 * recency)
        item = dict(r)
        item["recency_score"] = recency
        item["final_score"] = final
        ranked.append(item)

    ranked.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
    return ranked

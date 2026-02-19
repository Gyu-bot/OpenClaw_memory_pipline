from __future__ import annotations

from typing import Any


ALLOWED_TYPES = {"preference", "profile", "project_state", "task_rule", "do_not_store"}



def extract_candidates(text: str) -> dict[str, list[dict[str, Any]]]:
    """
    Phase 2 mock extractor.
    - LLM 호출 없이 규칙 기반으로 기억 후보를 만든다.
    - 추후 LLM extractor로 교체하되, 출력 포맷은 유지한다.
    """
    t = (text or "").strip()
    candidates: list[dict[str, Any]] = []

    if not t:
        return {"candidates": []}

    lowered = t.lower()

    # briefing style preference
    if "브리핑" in t and ("친근" in t or "대화" in t or "템플릿" in t):
        value = "친근한 대화체, 고정 템플릿 지양"
        if "금지" in t or "싫" in t or "말고" in t:
            value = "친근한 대화체, 고정 템플릿 금지"
        candidates.append(
            {
                "type": "preference",
                "key": "briefing_tone",
                "value": value,
                "confidence": 0.9,
                "evidence": t,
            }
        )

    # generic pattern: "X는/은 Y" => profile preference-ish fallback
    if ("는 " in t or "은 " in t) and len(candidates) == 0:
        candidates.append(
            {
                "type": "profile",
                "key": "user_fact",
                "value": t[:240],
                "confidence": 0.6,
                "evidence": t,
            }
        )

    # explicit do-not-store hints
    if any(k in lowered for k in ["비밀번호", "토큰", "api key", "api_key", "패스워드", "주민번호"]):
        candidates.append(
            {
                "type": "do_not_store",
                "key": "sensitive_hint",
                "value": "민감정보 포함 가능성",
                "confidence": 1.0,
                "evidence": t,
            }
        )

    # sanitize invalid type if ever introduced
    for c in candidates:
        if c["type"] not in ALLOWED_TYPES:
            c["type"] = "do_not_store"

    return {"candidates": candidates}

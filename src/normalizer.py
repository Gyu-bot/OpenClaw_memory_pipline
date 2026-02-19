from __future__ import annotations

import re
from typing import Any



def _canonical_key(raw_key: str) -> str:
    k = (raw_key or "").strip().lower()
    k = k.replace(" ", "_").replace("-", "_")
    k = re.sub(r"[^a-z0-9_]+", "", k)
    return k or "unknown_key"



def normalize_candidates(extract_out: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    normalized: list[dict[str, Any]] = []

    for c in extract_out.get("candidates", []):
        ctype = c.get("type")
        if ctype in {"do_not_store", None}:
            continue

        normalized.append(
            {
                "type": ctype,
                "canonical_key": _canonical_key(c.get("key", "")),
                "value": str(c.get("value", "")).strip(),
                "confidence": float(c.get("confidence", 0.0)),
            }
        )

    return {"normalized": normalized}

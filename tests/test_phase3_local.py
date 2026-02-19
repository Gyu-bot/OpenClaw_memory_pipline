from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reranker import rerank_results
from src.pipeline_read import _dedup_memories


def test_rerank_basic():
    results = [
        {"id": 1, "score": 0.6, "payload": {"confidence": 0.9}},
        {"id": 2, "score": 0.9, "payload": {"confidence": 0.5}},
    ]
    ranked = rerank_results(results)
    assert ranked[0]["id"] == 2
    assert "final_score" in ranked[0]
    assert "recency_score" in ranked[0]


def test_dedup_memories():
    arr = ["친근하게 해줘", "친근하게  해줘", "다르게 해줘"]
    out = _dedup_memories(arr)
    assert out == ["친근하게 해줘", "다르게 해줘"]

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reranker import rerank_results


def test_rerank_basic():
    results = [
        {"id": 1, "score": 0.6, "payload": {"confidence": 0.9}},
        {"id": 2, "score": 0.9, "payload": {"confidence": 0.5}},
    ]
    ranked = rerank_results(results)
    assert ranked[0]["id"] == 2
    assert "final_score" in ranked[0]

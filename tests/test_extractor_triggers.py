from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.extractor import extract_candidates


def test_positive_trigger_extracts():
    out = extract_candidates("기억해: 브리핑은 짧고 친근하게")
    assert any(c.get("type") == "task_rule" for c in out["candidates"])


def test_negative_trigger_blocks_storage():
    out = extract_candidates("이건 기억하지마: 임시 메모")
    assert not any(c.get("type") == "task_rule" for c in out["candidates"])


def test_low_information_blocks_storage():
    out = extract_candidates("이거 기억해")
    assert not any(c.get("type") == "task_rule" for c in out["candidates"])


def test_trailing_trigger_cleanup():
    out = extract_candidates("브리핑 톤은 친근하게 기억해")
    task = [c for c in out["candidates"] if c.get("type") == "task_rule"]
    assert task
    assert "기억해" not in task[0]["value"]

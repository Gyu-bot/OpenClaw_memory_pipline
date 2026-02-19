from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.extractor import extract_candidates
from src.normalizer import normalize_candidates
from src.validator import validate_memories


def test_phase2_local_flow():
    text = "브리핑은 템플릿 말고 친근하게 해줘"
    ext = extract_candidates(text)
    assert ext["candidates"], "extractor should produce at least one candidate"

    norm = normalize_candidates(ext)
    assert norm["normalized"], "normalizer should produce at least one normalized item"

    val = validate_memories(norm)
    assert len(val["accepted"]) >= 1, "validator should accept at least one item"

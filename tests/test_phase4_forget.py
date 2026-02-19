from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.maintenance import cleanup_fallback_expired


def test_cleanup_callable():
    removed = cleanup_fallback_expired()
    assert isinstance(removed, int)

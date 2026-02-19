#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync
uv run python -c "from src.maintenance import cleanup_fallback_expired; print({'removed': cleanup_fallback_expired()})"

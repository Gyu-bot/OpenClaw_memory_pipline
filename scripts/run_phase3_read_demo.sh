#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync
uv run python -m src.pipeline_read --query "브리핑 톤 기억" --user-id 982670783509852290

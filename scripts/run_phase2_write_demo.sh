#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync
uv run python -m src.pipeline_write --input tests/fixtures_write_input.json

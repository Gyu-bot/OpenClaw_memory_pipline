# CHANGELOG

## 2026-02-19

### Infrastructure
- Installed Qdrant on `docker-lab`
- Configured persistent storage at `/home/gyurin/qdrant_storage`
- Created collection `agent_memory` (vector size 1536, cosine)
- Enabled API key authentication and verified auth behavior (401 without key / 200 with key)

### Project setup (Phase 1)
- Created scaffold:
  - `schemas/`, `policy/`, `src/`, `tests/`, `scripts/`
- Added schemas:
  - `schemas/extract.output.schema.json`
  - `schemas/normalize.output.schema.json`
  - `schemas/validate.output.schema.json`
- Added policy files:
  - `policy/memory_policy.yaml`
  - `policy/sensitive_patterns.yaml`
- Added `tests/test_schemas.py`
- Added `scripts/run_phase1_check.sh`

### Python environment policy update
- Switched execution guidance to **uv only** (no pip/venv workflow)
- Added `pyproject.toml` and generated `uv.lock`
- Updated scripts/docs to use `uv sync` + `uv run`

### Repo management
- Moved project from workspace to:
  - `/home/gyurin/projects/memory_pipline`

### Documentation refresh for handoff
- Added detailed handoff instructions in `AGENTS.md`
- Rewrote `README.md` for project purpose/context
- Updated `STATUS.md` with current phase and next actions
- Updated `PROCESS_PLAN.md` (see latest task state references)

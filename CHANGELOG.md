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

### Phase 2 progress (write path PoC)
- Implemented:
  - `src/config.py`
  - `src/extractor.py` (rule-based mock extractor)
  - `src/normalizer.py`
  - `src/validator.py`
  - `src/embedder.py` (deterministic fake embedding for PoC)
  - `src/store_qdrant.py`
  - `src/pipeline_write.py`
- Added demo/test files:
  - `tests/fixtures_write_input.json`
  - `tests/test_phase2_local.py`
  - `scripts/run_phase2_write_demo.sh`
- Fixed YAML regex escaping in `policy/sensitive_patterns.yaml`
- Verified write path PoC end-to-end:
  - extraction -> normalization -> validation -> Qdrant upsert success

### Phase 3 progress (read path PoC)
- Implemented:
  - `src/retriever.py` (Qdrant search + user_id filter)
  - `src/reranker.py` (relevance + confidence score)
  - `src/pipeline_read.py` (retrieval -> rerank -> bounded memory output)
- Added:
  - `tests/test_phase3_local.py`
  - `scripts/run_phase3_read_demo.sh`
- Verified read path PoC:
  - query "브리핑 톤 기억" returned stored memory
  - debug output includes score/final_score and payload

### Phase 4 progress (operational safeguards)
- Implemented:
  - `src/audit_log.py` (jsonl audit trail)
  - `src/fallback_store.py` (local fallback read/write)
  - `src/maintenance.py` (fallback TTL cleanup)
  - `src/forget.py` (forget by key / forget by user)
- Enhanced pipelines:
  - `src/pipeline_write.py`: created_at/updated_at/expires_at payload, qdrant health fallback, audit events
  - `src/pipeline_read.py`: fallback path + audit events
- Added:
  - `tests/test_phase4_forget.py`
  - `scripts/run_phase4_cleanup.sh`
- Verified end-to-end after Phase 4 updates:
  - write demo success
  - read demo success
  - cleanup script success

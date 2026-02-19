# CHANGELOG

## 2026-02-19
- Added initial Phase 1 scaffold for `memory_pipeline`
- Added schema files:
  - `schemas/extract.output.schema.json`
  - `schemas/normalize.output.schema.json`
  - `schemas/validate.output.schema.json`
- Added policy files:
  - `policy/memory_policy.yaml`
  - `policy/sensitive_patterns.yaml`
- Added `tests/test_schemas.py` and `scripts/run_phase1_check.sh`
- Created local venv and verified schema tests pass

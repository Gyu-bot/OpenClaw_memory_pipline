# STATUS

- Updated: 2026-02-19 UTC
- Phase: 1 완료

## Done
- 폴더 구조 생성 (`schemas/`, `policy/`, `src/`, `tests/`, `scripts/`)
- JSON Schema 3종 작성
- 정책 파일 작성 (`memory_policy.yaml`, `sensitive_patterns.yaml`)
- `.env.example`, `requirements.txt`, `README.md` 작성
- 테스트 스크립트 작성 (`tests/test_schemas.py`)
- venv 생성 후 스키마 테스트 통과

## Next (Top 3)
1. `src/extractor.py` 최소 구현 (LLM 호출 없이 mock 입력부터)
2. `src/normalizer.py` canonical key/시간 정규화 규칙 구현
3. `src/validator.py` 민감패턴 + confidence 필터 구현

# STATUS

- Updated: 2026-02-19 UTC
- Current Phase: **1 완료 / 2 준비됨**

## Completed

### Project/Docs
- 프로젝트를 workspace 밖으로 이동:
  - `/home/gyurin/projects/memory_pipline`
- 핵심 문서 정리:
  - `README.md`, `PROCESS_PLAN.md`, `AGENTS.md`, `CHANGELOG.md`

### Phase 1 Artifacts
- 구조 생성: `schemas/`, `policy/`, `src/`, `tests/`, `scripts/`
- 스키마 3종 생성:
  - `extract.output.schema.json`
  - `normalize.output.schema.json`
  - `validate.output.schema.json`
- 정책 파일 생성:
  - `memory_policy.yaml`
  - `sensitive_patterns.yaml`
- uv 기반 설정:
  - `pyproject.toml`, `uv.lock`
  - 실행/검증 스크립트 uv 기준으로 통일
- 검증 완료:
  - `uv run python tests/test_schemas.py` 통과

### Infra
- Qdrant on `docker-lab` 설치/기동
- collection `agent_memory` 생성 (1536, cosine)
- API key 인증 활성화 및 검증 완료

## Next Top 3

1. `src/extractor.py` 구현
   - 입력 텍스트 -> schema 준수 `candidates` JSON 출력
2. `src/normalizer.py` 구현
   - canonical key 맵핑 + 시간/표현 정규화
3. `src/validator.py` + `src/pipeline_write.py` 구현
   - 민감정보/신뢰도 필터 후 Qdrant upsert

## Risks / Decisions Pending

- 방화벽으로 Qdrant 접근 범위를 내부망으로 추가 제한할지 여부
- 키 로테이션 주기 확정
- Phase 2에서 extractor를 LLM 실호출로 시작할지 mock-first로 시작할지

# STATUS

- Updated: 2026-02-19 UTC
- Current Phase: **4 완료 (OpenClaw 직접 통합 전 단계 완료)**

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

1. OpenAI embedding 실연동
   - `src/embedder.py` fake embedding -> 실제 API 호출 전환
2. OpenClaw 통합 PoC(Shadow mode)
   - write/read 훅 연결 및 실대화 영향 없는 병행 검증
3. 품질/운영 검증
   - 중복 제거, recency 강화, token budget 정밀화

## Risks / Decisions Pending

- 방화벽으로 Qdrant 접근 범위를 내부망으로 추가 제한할지 여부
- 키 로테이션 주기 확정
- Phase 2에서 extractor를 LLM 실호출로 시작할지 mock-first로 시작할지

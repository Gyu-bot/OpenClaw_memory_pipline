# AGENTS.md — Codex/Handoff Instructions for `memory_pipline`

이 저장소는 OpenClaw 메모리 자동화 파이프라인 PoC를 구현하기 위한 프로젝트다.

## Project Goal
OpenClaw 기본 메모리(core + memorySearch) 위에 아래 자동화 계층을 추가한다.

1. **Write path**: 대화 -> 기억 후보 추출 -> 정규화 -> 검증 -> 벡터 저장
2. **Read path**: 질의 -> 관련 기억 검색 -> 재랭킹 -> 프롬프트 주입

핵심 목표:
- 컨텍스트 품질 향상
- 토큰 낭비 감소
- 기억 오염/민감정보 저장 방지

---

## Non-Negotiables

- Python 환경/실행은 **uv만 사용** (`pip`, 수동 `venv` 금지)
- 민감정보(키/토큰/개인식별정보) 저장 금지
- 모든 변경은 `STATUS.md` + `CHANGELOG.md`에 기록
- 경로 기준은 현재 저장소 루트: `/home/gyurin/projects/memory_pipline`

---

## Runtime Context

### Vector DB
- Host: `docker-lab` (`192.168.1.15`)
- Qdrant URL: `http://192.168.1.15:6333`
- Collection: `agent_memory`
- Auth: API key enabled

### OpenClaw relationship
- 현재 OpenClaw는 `memory-core + memorySearch` 활성 상태
- 본 프로젝트는 별도 PoC로 진행 후, 안정화되면 Skill로 패키징 예정

---

## Phase Plan

### Phase 1 (Done)
- 구조/스키마/정책 고정

### Phase 2 (Next)
- `extractor.py`, `normalizer.py`, `validator.py`, `pipeline_write.py`
- 샘플 입력 -> accepted memory Qdrant upsert 성공

### Phase 3
- `retriever.py`, `reranker.py`, `pipeline_read.py`
- 질의 기반 top-k retrieval + bounded injection

### Phase 4
- forget/delete handling, audit logging, TTL cleanup, fallback

---

## Required Commands

```bash
cd /home/gyurin/projects/memory_pipline
uv sync
uv run python tests/test_schemas.py
```

Phase 2부터는 각 파이프라인 데모를 `scripts/`에 추가하고 아래처럼 실행 가능해야 함:

```bash
uv run python -m src.pipeline_write --input tests/fixtures/write_input.json
uv run python -m src.pipeline_read --query "..." --user-id 982670783509852290
```

---

## Definition of Done (per phase)

### Phase 2 DoD
- extractor/normalizer/validator 출력이 각 schema를 통과
- validator가 민감정보를 reject
- Qdrant upsert 성공 + payload 구조 검증

### Phase 3 DoD
- user_id 필터 기반 retrieval
- 재랭킹 점수 반영(관련도+최신성+신뢰도)
- 주입 토큰 상한 준수

### Phase 4 DoD
- "잊어줘" 삭제 플로우 동작
- 감사 로그로 저장/주입 근거 추적 가능
- 만료 memory 정리 잡 동작

---

## Coding Guidelines

- 함수는 단일 책임 유지
- 모든 외부 I/O는 thin wrapper로 분리 (`store_qdrant.py`, `embedder.py`)
- 정책값 하드코딩 금지 (`policy/*.yaml` 및 env에서 읽기)
- 에러 메시지는 운영자가 바로 이해 가능하게 작성

---

## Handoff Update Rules

작업 끝나면 반드시:
1. `STATUS.md` 갱신 (현재 phase, 다음 액션 1~3개)
2. `CHANGELOG.md` 갱신 (파일/동작 변경사항)
3. 필요한 경우 `PROCESS_PLAN.md`의 체크리스트 반영


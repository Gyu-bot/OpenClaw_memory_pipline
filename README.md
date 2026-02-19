# memory_pipline

OpenClaw 메모리 자동화 파이프라인 PoC 프로젝트.

> 최종 목표: 안정화 후 OpenClaw Skill 형태로 패키징.

## 왜 이 프로젝트를 하나?

기존 OpenClaw 메모리(`memory-core + memorySearch`)는 이미 유용하지만,
아래 자동화가 추가되면 운영 품질이 더 좋아진다.

- 기억 후보 자동 추출
- 키/시간/표현 정규화
- 민감정보/저신뢰 기억 차단
- 관련 기억만 재랭킹해 주입

즉, “무작정 다 기억”이 아니라 **안전하고 품질 높은 기억 자동화**를 목표로 한다.

---

## 현재 상태

- Phase 1 완료 (스키마/정책/프로젝트 골격)
- Qdrant 인프라 준비 완료 (`docker-lab`, API key enabled)
- 다음 단계: Phase 2 (Write path 구현)

---

## 디렉터리 구조

- `schemas/` — 단계별 출력 JSON schema
- `policy/` — 저장 정책/민감정보 패턴
- `src/` — 파이프라인 코드
- `tests/` — 검증 테스트
- `scripts/` — 실행 스크립트
- `PROCESS_PLAN.md` — 상세 설계/운영 계획
- `AGENTS.md` — 코딩 에이전트 작업 지침
- `STATUS.md` — 현재 진행 상태
- `CHANGELOG.md` — 변경 이력

---

## 환경 준비 (uv only)

```bash
cd /home/gyurin/projects/memory_pipline
uv sync
```

테스트:

```bash
uv run python tests/test_schemas.py
# 또는
./scripts/run_phase1_check.sh
```

---

## 주요 환경변수

```bash
QDRANT_URL=http://192.168.1.15:6333
QDRANT_COLLECTION=agent_memory
QDRANT_API_KEY=<set>

OPENAI_API_KEY=<set>
MEMORY_EMBEDDING_MODEL=text-embedding-3-small
MEMORY_CHAT_MODEL=gpt-5.3-codex

MEMORY_TOP_K=6
MEMORY_MIN_CONFIDENCE=0.75
MEMORY_MAX_INJECT_TOKENS=1200
MEMORY_ENABLE_WRITE=true
MEMORY_ENABLE_READ=true
```

참고: `MEMORY_CHAT_MODEL`은 OpenClaw 기본 키가 아니라 이 프로젝트 파이프라인에서 쓰는 커스텀 키다.

---

## 실행 로드맵

1. **Phase 2**: extractor/normalizer/validator + write pipeline
2. **Phase 3**: retriever/reranker + read pipeline
3. **Phase 4**: 삭제/감사로그/정리잡 + fallback
4. 안정화 후 Skill 승격

상세는 `PROCESS_PLAN.md` 참고.

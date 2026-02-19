# Memory Pipeline 구현 계획 / 작업 관리 문서

작성일: 2026-02-19 (UTC)
최종 수정: 2026-02-19 (UTC)

---

## 0) 프로젝트 취지 (왜 필요한가)

이 프로젝트는 OpenClaw의 기존 메모리(`memory-core + memorySearch`)를 대체하려는 것이 아니라,
그 위에 **안전한 자동화 계층**을 추가해 실제 운영 품질을 높이기 위한 PoC다.

핵심 문제:
- 중요한 컨텍스트를 사람이 매번 수동 기록해야 함
- 무분별한 기억 저장 시 오염/민감정보 리스크
- 질의 시 관련 기억만 정확히 주입하기 어려움

핵심 목표:
1. 자동 후보 추출
2. 정규화/검증으로 품질 보장
3. 관련 기억만 재랭킹 후 제한적으로 주입

---

## 1) 현재 컨텍스트 (빠른 브리핑)

## OpenClaw 측
- 기존 메모리 시스템 활성화 상태 유지 (`memory-core + memorySearch`)
- 본 프로젝트는 별도 디렉토리에서 독립 개발

## 인프라 측
- Qdrant 설치 위치: `docker-lab` (`192.168.1.15`)
- 컬렉션: `agent_memory` (1536, Cosine)
- API key 인증 활성화 완료

## 프로젝트 위치
- `/home/gyurin/projects/memory_pipline`

---

## 2) 목표 아키텍처

```text
[Write Path]
Conversation/Event
  -> Extractor
  -> Normalizer
  -> Validator
  -> Embedder
  -> Qdrant Upsert

[Read Path]
User Query
  -> Query Embed
  -> Qdrant Search (user_id filter)
  -> Reranker (relevance + recency + confidence)
  -> Prompt Injection (token budget bound)
```

---

## 3) 데이터/정책 기준

## 허용 타입
- preference
- profile
- project_state
- task_rule

## 금지
- API 키/토큰/비밀번호
- 결제/식별 민감정보
- 운영상 불필요한 일회성 잡담

## 기본 정책
- min_confidence: 0.75
- TTL:
  - project_state: 30일
  - task_rule: 14일
  - preference/profile: 무기한(수동 삭제 전)
- top_k: 6
- max_inject_tokens: 1200

---

## 4) 단계별 상세 구현

## Phase 1 (완료)
- 스키마/정책/폴더 구조 확정
- uv 기반 실행체계 확정
- 스키마 테스트 통과

## Phase 2 (다음)

목표: Write path end-to-end 구현

구현 파일:
- `src/extractor.py`
- `src/normalizer.py`
- `src/validator.py`
- `src/embedder.py`
- `src/store_qdrant.py`
- `src/pipeline_write.py`

DoD:
- 샘플 입력 -> validated accepted items 생성
- accepted items Qdrant upsert 성공
- 민감정보 포함 케이스 reject 확인

## Phase 3

목표: Read path 구현

구현 파일:
- `src/retriever.py`
- `src/reranker.py`
- `src/pipeline_read.py`

DoD:
- user_id 필터 검색
- 재랭킹 결과 상위 n개 반환
- 프롬프트 주입량 제한 준수

## Phase 4

목표: 운영 안정화

구현 항목:
- forget/delete 핸들러
- 감사 로그
- TTL cleanup job
- fallback 경로(기존 메모리 체계)

DoD:
- 저장/주입/삭제 이력 추적 가능
- 장애 시 graceful fallback

---

## 5) 코딩 에이전트(Codex) 작업 규칙

1. 항상 `AGENTS.md` 먼저 확인
2. Python 작업은 uv만 사용
3. 정책값 하드코딩 금지
4. 변경 후 `STATUS.md`, `CHANGELOG.md` 갱신
5. 보안 관련 변경은 근거와 함께 문서화

---

## 6) 실행 커맨드 기준

```bash
cd /home/gyurin/projects/memory_pipline
uv sync
uv run python tests/test_schemas.py
```

Phase 2 이후 expected demo:

```bash
uv run python -m src.pipeline_write --input tests/fixtures/write_input.json
uv run python -m src.pipeline_read --query "브리핑 스타일" --user-id 982670783509852290
```

---

## 7) Skill화 전략

결론: **최종적으로 Skill화 권장**

이유:
- OpenClaw 세션 재시작/서브에이전트에서도 일관 실행
- 규칙/정책/스크립트 재사용 가능
- 운영 안정화 후 배포 단위 명확

권장 흐름:
1. 현재 프로젝트에서 PoC/안정화
2. Phase 4 완료 후 Skill 구조로 포장
3. workspace skills 경로로 재배치

---

## 8) 중단/재개 체크포인트

중단 시:
- `STATUS.md`에 현재 작업 파일과 다음 액션 기록
- `CHANGELOG.md`에 변경 내역 기록

재개 시:
1. `AGENTS.md`
2. `STATUS.md`
3. `PROCESS_PLAN.md`
4. 마지막 커밋/변경 파일

위 순서로 확인 후 진행.

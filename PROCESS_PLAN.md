# Memory Pipeline 구현 계획 / 작업 관리 문서

작성일: 2026-02-19 (UTC)
작성자: 규봇

---

## 0) 문서 목적

이 문서는 아래 목적을 위해 만든 **작업 기준서**다.

1. 메모리 파이프라인(추출기/정규화기/검증기/저장기/조회기) 구현 과정을 명확히 관리
2. 작업 중단/재개 시 현재 상태를 빠르게 파악
3. 민규님이 진행 상황과 결정 사항을 한눈에 이해

---

## 1) 현재 완료 상태 (as-is)

### 인프라
- [x] Qdrant 설치 완료 (host: `docker-lab`)
- [x] 컨테이너 실행 중 (`qdrant/qdrant:latest`)
- [x] 데이터 영속 경로: `/home/gyurin/qdrant_storage`
- [x] 컬렉션 생성: `agent_memory` (vector size: 1536, distance: Cosine)
- [x] 샘플 upsert/search 동작 확인
- [x] API Key 인증 활성화 확인 (무키 401 / 키 포함 200)

### 환경변수
- [x] `QDRANT_URL` 주입됨
- [x] `QDRANT_API_KEY` 주입됨
- [ ] (권장) 운영 시 키 로테이션 정책 확정

---

## 2) 목표 아키텍처 (to-be)

```text
[대화 입력]
   -> Extractor (기억 후보 추출)
   -> Normalizer (정규화)
   -> Validator (정책/민감정보 검증)
   -> Embedder (임베딩)
   -> Qdrant Upsert (저장)

[질문 입력]
   -> Query Embed
   -> Qdrant Search (user_id 필터)
   -> Rerank (관련도+최신성+신뢰도)
   -> Prompt Injection (토큰 예산 내 주입)
```

핵심 원칙:
- 자동 저장은 하되, 저장 범위를 엄격히 제한
- 민감정보 저장 금지
- 주입량 제한으로 응답 품질/속도 유지

---

## 3) 기억 데이터 스키마 (초안)

## 3.1 내부 표준 메모리 레코드

```json
{
  "id": "uuid",
  "user_id": "982670783509852290",
  "type": "preference",
  "canonical_key": "briefing_tone",
  "value": "친근한 대화체, 고정 템플릿 금지",
  "confidence": 0.93,
  "source": {
    "session_id": "main",
    "message_id": "1473949621666578502"
  },
  "created_at": "2026-02-19T07:40:00Z",
  "updated_at": "2026-02-19T07:40:00Z",
  "expires_at": null
}
```

## 3.2 허용 타입
- `preference`
- `profile`
- `project_state`
- `task_rule`

## 3.3 TTL 기본값
- `project_state`: 30일
- `task_rule`: 14일
- `preference/profile`: 만료 없음 (수동 삭제 전)

---

## 4) 구현 단계별 계획

## Phase 1 — 골격/정책/스키마

목표: 파이프라인 인터페이스와 규칙 고정

할 일:
- [ ] 디렉터리 구조 생성
- [ ] `schemas/*.json` 작성
- [ ] `policy/memory_policy.yaml` 작성
- [ ] `policy/sensitive_patterns.yaml` 작성
- [ ] `.env.example` 작성
- [ ] `README.md` 작성

완료 기준:
- JSON schema validation 통과
- 정책 파일만 보고 저장 허용/금지 기준 이해 가능

---

## Phase 2 — Write 파이프라인

목표: 대화 -> 저장까지 자동 처리

모듈:
- [ ] `src/extractor.py`
- [ ] `src/normalizer.py`
- [ ] `src/validator.py`
- [ ] `src/embedder.py`
- [ ] `src/store_qdrant.py`
- [ ] `src/pipeline_write.py`

완료 기준:
- 샘플 대화 입력 시 accepted 항목이 Qdrant에 저장
- 민감정보 케이스는 저장 거부

---

## Phase 3 — Read 파이프라인

목표: 질문 -> 관련 기억 검색/재랭크/주입

모듈:
- [ ] `src/retriever.py`
- [ ] `src/reranker.py`
- [ ] `src/pipeline_read.py`

완료 기준:
- 같은 user_id 기준으로 관련 기억 top-k 반환
- 토큰 예산(`MEMORY_MAX_INJECT_TOKENS`) 초과 방지

---

## Phase 4 — 운영 안정화

목표: 실제 운영 가능한 안전장치 추가

할 일:
- [ ] "잊어줘" 삭제 핸들러
- [ ] 감사 로그(왜 저장/주입됐는지)
- [ ] 만료/중복 정리 잡
- [ ] 장애 시 fallback(기존 메모리 시스템)

완료 기준:
- 삭제/정정/추적이 가능한 상태

---

## 5) To-Do 체크리스트 (실행용)

## 즉시 착수
- [ ] Phase 1 파일 생성
- [ ] 스키마 검증 스크립트 작성
- [ ] 샘플 입출력 fixture 작성

## 구현 중
- [ ] Write 경로 E2E 통합 테스트
- [ ] Read 경로 E2E 통합 테스트
- [ ] 성능/토큰 지표 측정 로깅

## 운영 전
- [ ] 민감정보 패턴 검토/보강
- [ ] TTL/보존 정책 최종 승인
- [ ] 내부망 접근 제한(방화벽) 확인

---

## 6) 중단/재개 운영 규칙

작업 중단 시 아래 파일을 갱신:
- `memory_pipeline/STATUS.md` (현재 단계, 다음 액션 1~3개)
- `memory_pipeline/CHANGELOG.md` (무엇을 바꿨는지)

재개 시 순서:
1. `PROCESS_PLAN.md` 확인
2. `STATUS.md` 확인
3. 마지막 변경 파일/테스트 로그 확인
4. 다음 액션부터 재시작

---

## 7) 의사결정 로그 (중요)

- 벡터DB는 Qdrant로 시작 (이유: 빠른 도입, 벡터 검색/필터 최적화)
- 운영 전략은 하이브리드:
  - 기존 OpenClaw 메모리(core + memorySearch) 유지
  - 신규 파이프라인은 단계적으로 병행
- 초기 자동 저장 스코프는 제한(4타입만)

---

## 8) 질문: Skill로 만들지, 프롬프트로 넣을지?

결론:
- **운영 자동화/재사용/유지보수까지 생각하면 Skill 형태가 더 좋음**
- 단순 실험/PoC면 프롬프트 주입만으로도 시작 가능

### 옵션 A) Skill 형태 (권장)
장점:
- 기능과 규칙을 파일/코드로 고정
- 재시작해도 일관성 유지
- 다른 세션/서브에이전트에서도 재사용 쉬움

적합한 경우:
- 장기 운영
- 반복 사용
- 팀/멀티 에이전트 확장

### 옵션 B) AGENTS.md/프롬프트 주입
장점:
- 시작이 빠름
- 실험하기 간단

한계:
- 규칙이 텍스트 지시 수준이라 변동성 큼
- 코드 기반 검증/테스트 체계가 약함

### 실무 추천
1. 빠른 PoC: 프롬프트 + 로컬 스크립트
2. 안정화: Skill 패키징으로 승격

---

## 9) 다음 액션 제안 (바로 실행 가능한 순서)

1) `memory_pipeline` 코드 골격 생성 (Phase 1)
2) Write 파이프라인 최소 동작 구현 (Phase 2)
3) Read 파이프라인 붙여서 주입 테스트 (Phase 3)
4) Skill 포장 여부 결정 (Phase 4 직전)

---

## 10) 참고 환경변수 키셋 (현재 기준)

```bash
QDRANT_URL=http://192.168.1.15:6333
QDRANT_COLLECTION=agent_memory
QDRANT_API_KEY=<set>

OPENAI_API_KEY=<set>
MEMORY_EMBEDDING_MODEL=text-embedding-3-small
MEMORY_CHAT_MODEL=gpt-5.3-codex   # 커스텀 변수(파이프라인 코드용)

MEMORY_TOP_K=6
MEMORY_MIN_CONFIDENCE=0.75
MEMORY_MAX_INJECT_TOKENS=1200
MEMORY_ENABLE_WRITE=true
MEMORY_ENABLE_READ=true
```

---

필요하면 다음 단계에서 `STATUS.md`, `CHANGELOG.md`, `TASKS.md`도 같이 자동 생성해서 바로 운영 가능한 형태로 맞추겠다.

# Code Review & Handover Document

작성일: 2026-02-19
대상: OpenClaw Memory Pipeline PoC (Phase 4 완료 시점)
목적: 코드 리뷰 결과 정리 + 다음 작업자(에이전트)에게 핸드오버

---

## 1. 전체 평가 요약

전반적으로 **잘 구조화된 PoC**다. 관심사 분리, 정책 외부화, fallback 설계 등이 깔끔하다.
하지만 실운영 전환 전에 반드시 수정해야 할 **버그 3건**, **보안 이슈 3건**, **설계 개선 10건+**이 확인되었다.

| 구분 | 건수 | 심각도 |
|------|------|--------|
| 버그 (데이터 손실/오동작 가능) | 3 | HIGH |
| 보안 이슈 | 3 | HIGH |
| 코드 품질/DRY 위반 | 3 | MEDIUM |
| 설계/아키텍처 개선 | 7 | MEDIUM |
| 테스트 부족 | 4 | MEDIUM |
| 문서 불일치 | 4 | LOW |

---

## 2. 버그 (HIGH — 반드시 수정)

### BUG-1: `new_point_id()` 동일 ID 충돌

- **파일**: `src/store_qdrant.py:46-47`
- **문제**: `int(time.time() * 1000)`으로 ID 생성 → `pipeline_write.py`의 for 루프에서 같은 밀리초에 여러 point가 생성되면 **동일 ID가 되어 이전 point를 덮어씀**
- **영향**: 한 메시지에서 2개 이상의 기억 후보가 추출되면 마지막 하나만 저장됨
- **수정 방안**: UUID4 사용 또는 밀리초 + 루프 인덱스 조합

```python
# 수정 예시
import uuid
def new_point_id() -> str:
    return str(uuid.uuid4())
```

### BUG-2: `forget.py`가 fallback store를 삭제하지 않음

- **파일**: `src/forget.py`
- **문제**: Qdrant에서만 삭제하고, `data/fallback_memories.jsonl`의 레코드는 삭제하지 않음
- **영향**: Qdrant 장애 중 저장된 데이터는 "잊어줘" 요청 후에도 계속 조회됨
- **수정 방안**: `forget_by_key()`, `forget_all_user()`에 fallback JSONL 필터링 로직 추가

### BUG-3: `read_fallback()`이 만료된 항목을 반환함

- **파일**: `src/fallback_store.py:18-33`
- **문제**: `expires_at` 확인 없이 user_id 매칭만으로 반환. `maintenance.py`의 정리 작업이 실행되기 전까지 만료 데이터가 읽힘
- **영향**: 이미 만료된 기억이 read pipeline에서 사용자에게 주입됨
- **수정 방안**: `read_fallback()` 내에서 `expires_at` 체크 추가

---

## 3. 보안 이슈 (HIGH)

### SEC-1: Qdrant 통신이 평문 HTTP

- **파일**: `.env.example:2`, `src/config.py:33`
- **문제**: `QDRANT_URL=http://192.168.1.15:6333` → API key가 평문 전송
- **수정 방안**: HTTPS 전환 또는 최소한 내부망 전용 확인 + 문서에 리스크 명시

### SEC-2: 감사 로그에 민감 데이터 포함 가능

- **파일**: `src/audit_log.py`
- **문제**: `payload`를 그대로 JSONL에 기록 → `evidence` 필드 등에 원문 텍스트가 포함될 수 있음
- **수정 방안**: 감사 로그에 기록할 필드를 화이트리스트 방식으로 제한

### SEC-3: `sensitive_patterns.yaml`의 `credit_card_like` 패턴이 너무 광범위

- **파일**: `policy/sensitive_patterns.yaml:10`
- **문제**: `\b(?:\d[ -]*?){13,19}\b`는 긴 숫자 ID, 타임스탬프, 전화번호 등도 매칭 → 정상 데이터의 오탐(false positive)
- **수정 방안**: Luhn 체크 또는 더 정밀한 패턴 적용, 또는 정규식 범위 축소

---

## 4. 코드 품질 / DRY 위반 (MEDIUM)

### DRY-1: `_request()` 함수 중복

- **파일**: `src/store_qdrant.py:10-21` / `src/retriever.py:11-20`
- **문제**: 완전히 동일한 HTTP 헬퍼가 두 파일에 복사되어 있음
- **수정 방안**: 공통 모듈(예: `src/http_client.py`)로 추출

### DRY-2: YAML 로딩 중복

- **파일**: `src/config.py:24-26` / `src/validator.py:13-15`
- **문제**: 같은 policy YAML을 `config.py`와 `validator.py`에서 각각 별도로 로딩
- **수정 방안**: `config.py`에서 한 번 로딩하고 전달하는 구조로 통합

### DRY-3: `ROOT` 경로 상수 산재

- **파일**: `src/config.py:11`, `src/validator.py:9`, `src/audit_log.py:8`, `src/fallback_store.py:7`, `src/maintenance.py:7`
- **문제**: 5개 파일에서 각각 `Path(__file__).resolve().parents[1]` 반복
- **수정 방안**: `config.py`의 `ROOT`를 import하여 재사용

---

## 5. 설계/아키텍처 개선 (MEDIUM)

### ARCH-1: 설정값 하드코딩

- **파일**: `src/pipeline_read.py:53,62`
- **문제**: `top_k=6`, `max_chars=1200`이 코드에 직접 박혀 있음. `AppConfig`에 `top_k`, `max_inject_tokens` 필드 없음
- **수정 방안**: `config.py`의 `AppConfig`에 `top_k`, `max_inject_tokens` 추가, policy YAML / env에서 로딩

### ARCH-2: `MEMORY_ENABLE_WRITE` / `MEMORY_ENABLE_READ` 미사용

- **파일**: `.env.example:15-16`
- **문제**: 환경변수로 정의되어 있지만 코드에서 읽지도, 체크하지도 않음
- **수정 방안**: `AppConfig`에 추가하고 파이프라인 진입부에서 체크 (feature flag)

### ARCH-3: 중복 저장 방지(Idempotency) 없음

- **문제**: 동일 메시지가 두 번 처리되면 동일한 기억이 중복 저장됨
- **수정 방안**: `(user_id, canonical_key)` 조합으로 기존 point 조회 후 upsert, 또는 message_id 기반 중복 체크

### ARCH-4: Qdrant TTL 정리 미구현

- **파일**: `src/maintenance.py`
- **문제**: fallback store의 TTL 정리만 구현됨. Qdrant에 저장된 만료 데이터는 영구 잔류
- **수정 방안**: Qdrant scroll + filter(`expires_at < now`) → delete 로직 추가

### ARCH-5: Qdrant upsert 실패 시 fallback 미작동

- **파일**: `src/pipeline_write.py:78-83`
- **문제**: `health_check()` 통과 후 `upsert_points()`에서 예외 발생 시 fallback 없이 exception 전파
- **수정 방안**: `upsert_points()` 호출을 try/except로 감싸고 실패 시 fallback 경로 진입

### ARCH-6: Reranker에 recency(최신성) 미반영

- **파일**: `src/reranker.py:12`
- **문제**: 주석에 "recency 추후 추가"라고 적혀있지만 미구현. `created_at` 필드가 payload에 존재하나 사용 안 함
- **수정 방안**: `final_score` 계산에 시간 감쇠(time decay) 가중치 추가

### ARCH-7: 파이프라인 입력 검증 없음

- **파일**: `src/pipeline_write.py:27`, `src/pipeline_read.py:27`
- **문제**: `user_id`가 빈 문자열이거나, `text`가 None일 때 등 방어 로직 없음
- **수정 방안**: 진입부에서 필수 파라미터 검증 + 명확한 에러 메시지

---

## 6. 테스트 부족 (MEDIUM)

### TEST-1: 테스트가 pytest를 사용하지 않음

- **파일**: `tests/test_schemas.py`
- **문제**: 스크립트 형태로 작성됨 (pytest discovery 불가). `test_phase2/3/4`는 함수 정의만 있고 실행하려면 pytest가 필요하지만 dependencies에 없음
- **수정 방안**: `pyproject.toml`에 pytest 추가, 모든 테스트를 pytest 규약으로 통일

### TEST-2: 테스트 커버리지 부족

현재 커버하지 않는 항목:
- 민감정보 탐지 (validator가 실제로 reject하는지)
- fallback store read/write 왕복
- forget 동작 (실제 삭제 검증 없이 "호출 가능" 수준만 테스트)
- pipeline_write / pipeline_read 통합 흐름
- 에러 케이스 (잘못된 입력, Qdrant 장애 시뮬레이션)

### TEST-3: `test_phase4_forget.py`가 의미 있는 검증을 하지 않음

- **파일**: `tests/test_phase4_forget.py`
- **문제**: `cleanup_fallback_expired()`가 `int`를 반환하는지만 확인. 실제로 만료 데이터가 제거되는지 검증하지 않음
- **수정 방안**: 테스트용 JSONL 데이터 생성 → cleanup → 결과 확인

### TEST-4: `test_schemas.py`가 스크립트 형태

- **문제**: pytest로 실행할 수 없고, `uv run python tests/test_schemas.py`로만 실행 가능
- **수정 방안**: 함수 형태로 변환 (`def test_...():`)

---

## 7. 문서 불일치 (LOW)

### DOC-1: 프로젝트 경로 불일치

- `README.md:47`, `AGENTS.md:23,62`, `PROCESS_PLAN.md:37,153`에서 `/home/gyurin/projects/memory_pipline` 참조
- 실제 경로와 다를 수 있음 (환경 의존적). 상대 경로 사용 권장

### DOC-2: 프로젝트명 오타 — "pipline" → "pipeline"

- 디렉토리 이름, README 제목 등에서 `memory_pipline`으로 표기 (l 누락)
- 리팩토링 시 정정 여부 결정 필요

### DOC-3: `AGENTS.md` 파일 경로 불일치

- `AGENTS.md:70`에서 `tests/fixtures/write_input.json` 참조
- 실제 파일은 `tests/fixtures_write_input.json` (디렉토리가 아닌 flat 파일)

### DOC-4: `README.md` / `STATUS.md` 상태 불일치

- `README.md:23-25`: "Phase 1 완료, 다음: Phase 2" (오래된 정보)
- `STATUS.md:4`: "Phase 4 완료" (최신)
- README 갱신 필요

---

## 8. 권장 작업 우선순위

### 즉시 수정 (P0)

| # | 항목 | 예상 난이도 |
|---|------|-----------|
| 1 | BUG-1: point ID 충돌 수정 | 쉬움 |
| 2 | BUG-2: forget에 fallback store 삭제 추가 | 보통 |
| 3 | BUG-3: read_fallback에 expires_at 체크 추가 | 쉬움 |
| 4 | ARCH-5: upsert 실패 시 fallback 추가 | 쉬움 |

### 보안 강화 (P1)

| # | 항목 | 예상 난이도 |
|---|------|-----------|
| 5 | SEC-2: 감사 로그 필드 화이트리스트 | 보통 |
| 6 | SEC-3: credit_card_like 정규식 정밀화 | 보통 |
| 7 | SEC-1: HTTPS 전환 또는 리스크 문서화 | 환경 의존 |

### 코드 품질 (P2)

| # | 항목 | 예상 난이도 |
|---|------|-----------|
| 8 | DRY-1: `_request()` 공통 모듈 추출 | 쉬움 |
| 9 | DRY-2, DRY-3: YAML 로딩/ROOT 통합 | 쉬움 |
| 10 | ARCH-1: 하드코딩 설정값 → AppConfig | 쉬움 |
| 11 | ARCH-2: feature flag 구현 | 쉬움 |
| 12 | ARCH-7: 입력 검증 추가 | 쉬움 |

### 기능 보강 (P3)

| # | 항목 | 예상 난이도 |
|---|------|-----------|
| 13 | ARCH-3: 중복 저장 방지 | 보통 |
| 14 | ARCH-4: Qdrant TTL 정리 | 보통 |
| 15 | ARCH-6: reranker recency 반영 | 보통 |
| 16 | TEST-1~4: 테스트 체계 전면 정비 | 보통 |
| 17 | DOC-1~4: 문서 갱신 | 쉬움 |

---

## 9. 핸드오버 에이전트 지침

### 작업 전 필수 확인

1. 이 문서 (`REVIEW_AND_HANDOVER.md`)
2. `AGENTS.md` — 코딩 규칙, 환경 정보
3. `STATUS.md` — 현재 진행 상태

### 수정 시 규칙

- Python 환경은 **uv만 사용** (pip/venv 금지)
- 수정 후 반드시 `STATUS.md`, `CHANGELOG.md` 갱신
- 정책값 하드코딩 금지 (policy YAML 또는 env에서 로딩)
- 기존 테스트가 깨지지 않도록 확인: `uv run pytest tests/`

### 수정하면 안 되는 것

- `schemas/*.json` — 스키마 변경은 별도 논의 필요
- `policy/memory_policy.yaml` — 정책 변경은 소유자 승인 필요
- Qdrant 인프라 설정 — 운영 환경이므로 직접 변경 금지

### 파일별 의존 관계

```
config.py ← 모든 모듈이 참조
embedder.py ← pipeline_write, retriever
store_qdrant.py ← pipeline_write, forget
retriever.py ← pipeline_read
extractor.py ← pipeline_write
normalizer.py ← pipeline_write
validator.py ← pipeline_write
reranker.py ← pipeline_read
audit_log.py ← pipeline_write, pipeline_read, forget
fallback_store.py ← pipeline_write, pipeline_read, maintenance
```

---

## 10. 참고: 현재 소스 파일별 줄 수

| 파일 | 줄 수 | 역할 |
|------|-------|------|
| `config.py` | 39 | 설정 로딩 |
| `extractor.py` | 69 | 규칙 기반 추출 (mock) |
| `normalizer.py` | ~34 | 키/값 정규화 |
| `validator.py` | 71 | 정책 검증 + 민감정보 차단 |
| `embedder.py` | 19 | fake embedding (PoC) |
| `store_qdrant.py` | 48 | Qdrant HTTP wrapper |
| `retriever.py` | 51 | Qdrant 검색 |
| `reranker.py` | 25 | 재랭킹 |
| `pipeline_write.py` | 113 | Write 오케스트레이터 |
| `pipeline_read.py` | 96 | Read 오케스트레이터 |
| `audit_log.py` | 21 | 감사 로깅 |
| `fallback_store.py` | 34 | 로컬 JSONL 저장소 |
| `forget.py` | 50 | 삭제 핸들러 |
| `maintenance.py` | 50 | TTL 정리 |

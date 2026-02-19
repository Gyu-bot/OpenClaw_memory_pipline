# Production Readiness Checklist (Go/No-Go)

작성일: 2026-02-19
대상: OpenClaw Memory Pipeline (Skill 전환 전 최종 점검)

사용법:
- 각 항목을 `YES`로 채워야 다음 단계 진행
- 섹션별 `필수 게이트` 중 하나라도 `NO`면 배포 보류

---

## 0) 배포 단계 정의

- Stage 0: Local PoC
- Stage 1: Shadow mode (실답변 비영향)
- Stage 2: Partial enable (일부 기능 활성)
- Stage 3: Full enable (실사용)

---

## 1) 정책/데이터 품질 게이트 (필수)

- [ ] YES / [ ] NO — 실시간 저장은 명시 트리거("기억해") 기반으로만 동작한다.
- [ ] YES / [ ] NO — 자동 저장(일일 리뷰)은 daily memory 기반으로만 수행한다.
- [ ] YES / [ ] NO — 저장 허용 타입(preference/profile/project_state/task_rule)이 코드/문서/정책에서 일치한다.
- [ ] YES / [ ] NO — 민감정보 차단 정책이 테스트로 검증되었다.
- [ ] YES / [ ] NO — 중복 저장 방지(idempotency) 로직이 작동한다.
- [ ] YES / [ ] NO — 충돌 규칙(명시 저장 > 자동 리뷰, 최신 우선)이 구현/문서화되었다.

필수 게이트 결과: [ ] PASS / [ ] FAIL

---

## 2) 보안 게이트 (필수)

- [ ] YES / [ ] NO — Qdrant 접근이 내부망 제한 또는 TLS로 보호된다.
- [ ] YES / [ ] NO — `QDRANT_API_KEY`가 적용되고 무키 접근 차단(401) 확인됐다.
- [ ] YES / [ ] NO — 감사 로그는 화이트리스트 필드만 기록한다.
- [ ] YES / [ ] NO — `잊어줘` 삭제가 Qdrant + fallback 모두 반영된다.
- [ ] YES / [ ] NO — 로그/백업 보존기간 및 삭제 정책이 문서화됐다.

필수 게이트 결과: [ ] PASS / [ ] FAIL

---

## 3) 안정성/복구 게이트 (필수)

- [ ] YES / [ ] NO — Qdrant 장애 시 fallback write/read가 정상 동작한다.
- [ ] YES / [ ] NO — upsert 예외 시 fallback 전환이 테스트로 검증됐다.
- [ ] YES / [ ] NO — 만료 데이터 정리(cleanup)가 정기적으로 실행된다.
- [ ] YES / [ ] NO — Cron 실패 감지/알림/재시도 경로가 있다.
- [ ] YES / [ ] NO — 즉시 off 가능한 kill switch(`MEMORY_ENABLE_WRITE/READ`)가 동작한다.

필수 게이트 결과: [ ] PASS / [ ] FAIL

---

## 4) 검색 품질 게이트 (필수)

- [ ] YES / [ ] NO — recency 점수가 최종 랭킹에 반영된다.
- [ ] YES / [ ] NO — top_k, 주입 예산(max_inject_tokens)이 설정 기반으로 동작한다.
- [ ] YES / [ ] NO — 중복 결과 제거(dedup) 후 주입한다.
- [ ] YES / [ ] NO — 대표 쿼리셋에서 기대 결과가 재현된다.

필수 게이트 결과: [ ] PASS / [ ] FAIL

---

## 5) 임베딩/비용 게이트

- [ ] YES / [ ] NO — 임베딩 API 실연동이 안정적으로 동작한다.
- [ ] YES / [ ] NO — 임베딩 캐시(hit/miss) 로깅이 가능하다.
- [ ] YES / [ ] NO — 캐시 TTL/용량 정책이 있다.
- [ ] YES / [ ] NO — API 장애/타임아웃 백오프가 있다.

---

## 6) 테스트 게이트

- [ ] YES / [ ] NO — 단위 테스트(validator/reranker/fallback/forget) 통과
- [ ] YES / [ ] NO — 통합 테스트(write->read->forget->cleanup) 통과
- [ ] YES / [ ] NO — 실패 시나리오 테스트(Qdrant down, API fail) 통과
- [ ] YES / [ ] NO — 회귀 테스트 세트가 준비됨

---

## 7) 관측/운영 게이트

- [ ] YES / [ ] NO — 핵심 지표 대시보드/로그 확인 가능
  - 저장 수 / reject 수 / 민감 차단 수
  - read 주입 수 / fallback 비율
  - 임베딩 호출 수 / 캐시 hit rate
- [ ] YES / [ ] NO — 운영 런북(장애 대응 문서) 존재
- [ ] YES / [ ] NO — 담당자/롤백 절차 정의 완료

---

## 8) Skill 패키징 게이트 (배포 직전)

- [ ] YES / [ ] NO — `SKILL.md` 작성 완료 (목적/명령/주의사항)
- [ ] YES / [ ] NO — skill entrypoint 명령 확정 (`remember`, `forget`, `review-daily`, `read-debug`)
- [ ] YES / [ ] NO — workspace skills 경로 배치 리허설 완료
- [ ] YES / [ ] NO — Shadow mode 결과 기준 충족

---

## 9) 최종 Go/No-Go

- 정책/보안/안정성/검색품질 4개 필수 게이트 모두 PASS인가?
  - [ ] YES -> Stage 3(Full enable) 진행
  - [ ] NO -> 보류, FAIL 항목 우선 수정

최종 판정: [ ] GO / [ ] NO-GO
판정 일시: ____________________
판정자: ____________________

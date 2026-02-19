# memory_pipeline

메모리 자동화 파이프라인 (Phase 1)

## 목적
대화에서 기억 후보를 추출/정규화/검증한 뒤 저장하고, 질의 시 관련 기억을 검색/주입하기 위한 기반 구조.

## 현재 단계
- Phase 1 완료 목표: 스키마/정책/환경변수/기본 구조 확정

## 구조
- `schemas/`: 각 단계 출력 스키마
- `policy/`: 저장 허용/금지/TTL/민감정보 패턴
- `src/`: 파이프라인 코드 (Phase 2부터 본격 구현)
- `tests/`: 스키마/정책 검증 테스트
- `scripts/`: 데모 실행 스크립트

## 빠른 확인 (uv)
```bash
cd /home/gyurin/.openclaw/workspace/memory_pipeline
uv sync
uv run python tests/test_schemas.py
```

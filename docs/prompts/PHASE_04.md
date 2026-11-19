# PHASE 04 — 분석·보고서

## AI 코딩 도구에 전달할 지시
`docs/MASTER_SPEC.md`, 관련 세부 명세서, `docs/TASKS.md`, `docs/PROGRESS.md` 및 `ORIGINAL_kotra.md`를 먼저 읽어라. 현재 저장소의 실제 파일을 확인한 뒤에만 구현 상태를 판단하라.

**목표:** BFS/EWS/대체 후보·3형식 출력.
**산출물:** analysis engines, document model, renderers.
**검수:** 3-Hop, 근거, 3x3 export.

## 필수 실행 규칙
1. 작업을 1~3개 작은 티켓으로 분해하고 각 티켓의 수정 파일·테스트를 먼저 제시.
2. 실데이터·출처·좌표·납품관계·통계를 만들어내지 말 것. synthetic은 명시된 테스트 fixture에서만 사용.
3. 현재 Python/SQLite/Vanilla JS 유지, 새로운 의존성은 근거와 버전 고정.
4. 기존 작동 기능을 삭제하거나 API 계약을 임의 변경하지 말 것. 변경이 필요하면 명세와 테스트를 함께 수정.
5. 실패·미구현·검증 불가를 숨기지 말 것. 실제 테스트 명령을 실행하고 결과를 기록.
6. 끝나면 `docs/TASKS.md` 체크 및 `docs/PROGRESS.md`에 변경 파일, 검수 결과, 남은 블로커를 기록.
7. 이번 Phase 외 범위는 구현하지 말 것. 다음 Phase의 필요조건만 명시.

## 완료 보고 형식
완료 티켓 / 수정 파일 / 실행 명령 / 통과·실패 테스트 / 실제 데이터 건수(해당 시) / 남은 문제 / 다음 티켓.

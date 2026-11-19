# 개발 로드맵
| Phase | 순서 | 핵심 산출물 | 완료 게이트 |
|---|---|---|---|
| 00 | 설계 고정 | SQL DDL, 데이터 사전, API schema, 테스트 계획 | 문서 모순 해소 |
| 01 | 대규모 실제 데이터 | source catalog, raw/staging/curated, provenance | 출처·수집 이력 검증 |
| 02 | DB/FTS | migrations, indexes, loader, validate CLI | FK/중복/검색 통과 |
| 03 | 백엔드 | REST API, pagination, search, admin import | 계약 테스트 통과 |
| 04 | 분석·보고 | BFS, EWS rule, alternatives, 3종×3포맷 | E2E 분석/출력 통과 |
| 05 | 프론트엔드 | 디자인 시스템, 홈+7화면, 지도·네트워크 | 브라우저·시각 검수 |
| 06 | 관리자·통합 QA | CSV 관리, 이력, 성능/접근성 | P0/P1 통과 |
| 07 | 향후 운영 | AI, 스케줄러, 로그인/RBAC, 배포 | 별도 운영 승인 |

각 Phase를 작은 티켓으로 나눠 **한 티켓에 하나의 검증 가능한 변경**만 적용. 실패한 테스트를 우회하는 목 데이터·조건문을 금지. 실제 확보 데이터량과 진행률은 매 작업 후 기록.

# 05 UI/UX 구현 명세
## 디자인 토큰
Modern Hybrid. Canvas `#F5F7FB`, surface `#FFFFFF`, navy `#0B1730`, primary `#2563EB`, teal `#0F766E`, border `#E9EFF7`. EWS는 alert/red, caution/orange, watch/yellow, normal/green; 검증 상태는 별도 아이콘/텍스트. Pretendard 또는 Noto Sans KR(로컬 대체), 숫자 Inter/system. sidebar 240/72px, header 64px, 12–16px radius, spacing 4/8/12/16/24/32px, transition 150–250ms. `prefers-reduced-motion` 지원, 키보드·포커스·대비 검증.
## 전역 구성
좌측 8개 메뉴, 상단 통합검색/지역/산업/기간/알림, 우측 400–480px 드릴다운 패널. URL query에 필터·선택 엔티티 동기화; 뒤로가기·북마크 가능. 필터 변경은 지도·KPI·테이블·차트에 일관 적용. 데이터 신선도·출처·검증 상태 항상 접근 가능.
## 8개 화면과 데이터 계약
0 홈: KPI `/overview`, 대형 2D 지도 `/facilities`, 산업 비교 `/overview`, 위험 `/events`, 최근 기사 `/evidence/search`. 지도 60~65%, 보조 분석 35~40%; KPI 클릭 → 필터된 상세 화면.
1 기업과 시설: 좌측 시설 지도 `/facilities`, 우측 관계 `/network`, 하단 `/companies` 테이블. 마커/노드/관계선 클릭 → `/detail` + 근거 패널.
2 지역과 산업: 7+1 권역×13 산업 매트릭스, 셀 클릭→품목 8필러 `/products/{id}/brief` 및 `/alternatives`. CA 전체는 benchmark로 분리.
3 수치 데이터: `/trade-stats`, 기간·단위·집계 기준별 시계열, 월간/누적/연간 혼합 차트 금지, 통화/환율 주석 표시.
4 사건과 위험: `/events` 활성·과거 재연 분리, `/ews` 위험 테이블, 사건 스레드 타임라인, 변경 시 이유 기록.
5 분석과 보고서: `/analyze`, `/network`, `/reports`; 좌측 조건, 중앙 위험 카드·경로, 우측 근거·추천·보고서 편집, HTML/PDF/DOCX 출력.
6 자료와 근거: `/evidence/search`, `/search/query`; 키워드·자연어 패턴 검색, 출처 등급/검증 상태 필터, 검색 근거와 검색 한계 표시.
7 관심 대상과 알림: `/reminders`, 관심 기업·품목, 규제 D-Day, 완료 상태 및 필터.
별도 Admin: CSV preview→validate→commit, 수집 실행 기록, 검증 대기, 수정 이력, 시스템 상태, 운영 시 사용자 권한.
## 지도 구현
실제 GeoJSON 경계만 사용; EPSG:4326 원본 좌표를 지도 투영에 맞게 변환, 좌표 불명 시설은 지도에서 제외하고 목록에 별도 표시. pan/zoom, bbox 질의, cluster, 마커 hover/선택, 데이터량 많으면 서버 집계. GeoJSON·마커의 출처 메타 제공. 임의 도로·물류 회랑 선 작도 금지.
## 네트워크 구현
1–3 Hop, 방향 화살표, 공급/투자/제휴 엣지 타입별 스타일, 검증/미검증 실선·점선, 드래그/줌/포커스/선택경로 강조. 대규모 그래프는 초기 노드 수 제한과 점진적 확장. 관계 클릭 시 근거가 없으면 '확인되지 않음' 명시.
## 상태 및 반응형
모든 화면 loading skeleton, empty state, error+retry, partial+stale, no-permission, source-unverified 표시. 1440/1024/768/390px 검수; 좁은 화면은 사이드바 접고 차트/지도 단일 열 전환. 테이블 정렬/페이지네이션, 필터 초기화, 모달 ESC 닫기, 네트워크 키보드 대체 목록 제공.
## 접근성·시각 검수
텍스트 대비, 포커스 링, 화면읽기 label, hover-only 정보 금지, 과도한 모션 억제, 지도/그래프 텍스트 대체. 스크린샷 비교와 브라우저 E2E를 모두 수행.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

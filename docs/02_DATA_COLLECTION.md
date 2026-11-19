# 02 데이터 수집 및 출처
## 공간 기준
권역: US-WA, US-OR, US-ID, US-MT, US-AK, US-CA-NORTH, US-CA-BAY9, US-CA(benchmark). `US-CA-NORTH`는 아래 22개 카운티의 프로젝트 자체 정의: Del Norte, Siskiyou, Modoc, Humboldt, Trinity, Shasta, Lassen, Tehama, Plumas, Mendocino, Glenn, Butte, Sierra, Nevada, Yuba, Placer, Colusa, Sutter, Lake, Yolo, El Dorado, Sacramento. Bay9: Alameda, Contra Costa, Marin, Napa, San Francisco, San Mateo, Santa Clara, Solano, Sonoma. 실제 적재 전 카운티 FIPS와 공식 GIS 경계를 검증. CA 전체 지표를 하위 권역 지표에 대입·합산 금지. 다른 CA 카운티는 두 세부 권역에 속하지 않음.
## 산업 13종
반도체; AI·ICT; 항공우주; 바이오·헬스; 포토닉스·광학; 첨단·일반 제조; 석유·가스; 광업·핵심광물; 전력·재생에너지; 임산업; 농식품; 수산; 물류·항만. 다중 산업 태깅 허용, 산업코드 사전 유지.
## 소스 카탈로그
우선: Census/BEA/BLS/USITC/SEC, Federal Register, USGS/NWS/FEMA, EIA/NOAA/USDA, NWSA 및 주정부 GIS·기업 공시. 원본의 Reuters/Bloomberg/Seattle Times 등은 라이선스/로봇 정책 검토 후 링크·허용된 메타데이터만 저장. 모든 소스는 접근 방식, 범위, 라이선스, 갱신주기, 수집일, 상태를 기록.
## 파이프라인
(1) 수집원 등록 (2) 다운로드/메타데이터 (3) 원문 해시·불변 저장 (4) 파싱·staging (5) 필드/단위/날짜/지역 검증 (6) 중복·별칭 매칭 (7) verified/reported/unverified/estimated/synthetic 상태 부여 (8) curated 적재 (9) 인덱스 갱신 (10) 로그·오류 기록.
## 필수 provenance
`source_url`, `publisher`, `published_at`, `retrieved_at`, `license_note`, `content_sha256`, `source_type`, `validation_status`, `evidence_tier`, `extraction_method`, `raw_path`, `batch_id`. 미확인 값은 NULL과 `missing_fields`로 보존; 출처를 임의 생성하지 말 것.
## 규모 및 우선순위
최대한 많이 수집하되 유효한 독립 레코드와 중복 복제·검색 청크를 구분. 실제 수집 완료 수량은 매니페스트에서 자동 산출. 초기 데이터 수집은 기업·시설·공급망, 경제·교역, 위험·규제 3영역을 균형 있게 진행. 최신 및 장기 시계열 모두 확보. 소스별 권리·요청 제한 준수.
## 데이터 품질 게이트
필수키, 참조무결성, 시간/통화/단위, 카운티 FIPS, 좌표 유효성, 중복률, 출처 연결률, null 비율, 검증상태 분포를 자동 보고. 미검증은 수집 가능하지만 자동 공식 경보 단독 근거 금지. `synthetic`은 별도 namespace/seed와 UI 배지로 분리.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

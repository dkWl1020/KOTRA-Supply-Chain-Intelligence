# 파일별 수용 기준

이 문서는 첨부 목록의 54개 항목을 실제 산출물과 연결한다. 아래 기준은 완료 여부를 판단하는 기준이며, 표에 있다는 이유만으로 기능이 운영 검증을 통과했다는 뜻은 아니다. 실제 데이터 수와 검사 결과는 최종 검증 기록을 함께 본다.

운영 테이블은 CSV를 수동 작성하지 않고 실행 중 DB에 생성한다. 조건부 자료는 유효한 근거를 확보했을 때 채우며, 빈 파일을 임의 사실로 채우지 않는다.

| 번호 | 원래 항목 | 산출물 위치 | 수용 기준 |
| --- | --- | --- | --- |
| 1 | regions.csv | data/regions.csv | 7개 조사 권역과 주·카운티를 구분하고 상위 지역 ID가 존재함. 북부 캘리포니아와 주 전체를 혼용하지 않음 |
| 2 | region_memberships.csv | data/region_memberships.csv | 포함 지역의 실제 ID가 존재함. 베이 9개와 북부 40개의 범위를 서로 대체하지 않음 |
| 3 | industries.csv | data/industries.csv | 13개 산업과 3개 클러스터를 유지하고 중복 ID가 없음 |
| 4 | companies.csv | data/companies.csv | 법인·기관·브랜드를 구분하고 공식 이름·국가·웹 주소를 보존함 |
| 5 | facilities.csv | data/facilities.csv | 운영사·지역이 존재하고 시설명·기능을 구분함. 좌표가 있으면 위치 정밀도와 근거를 해석할 수 있음 |
| 6 | products.csv | data/products.csv | 소재·부품·완제품·서비스의 명칭이 일관되고 활동의 품목 ID가 연결됨 |
| 7 | activities.csv | data/activities.csv | 기업·산업·품목·시설의 유효 ID를 사용하고 실제 역할과 잠재 수요를 구분함 |
| 8 | statistics.csv | data/statistics.csv | 기간·단위·수치 유형·범위·원문이 연결됨. 빈칸과 0이 구분되고 잘못된 단위를 적재하지 않음 |
| 9 | projects.csv | data/projects.csv | 총사업비·지원액·개별 단계 투자와 발표·건설·가동 단계를 구분함 |
| 10 | relationships.csv | data/relationships.csv | 관계 방향·유형·근거가 있으며 특정 공장 관계는 시설 근거가 있을 때만 연결함 |
| 11 | routes.csv | data/routes.csv | 일반 연결·서비스·실제 이용·대체 제안의 구분이 있음 |
| 12 | route_segments.csv | data/route_segments.csv | 경로 내 순번이 중복되지 않고 출발·도착 거점과 운송수단이 일관됨 |
| 13 | risk_profiles.csv | data/risk_profiles.csv | 위험 대상이 실제로 존재하고 구조적 노출을 실제 피해로 표현하지 않음 |
| 14 | events.csv | data/events.csv | 발생·발표·종료 시점과 상태를 구분함. 과거 사건은 재연 자료로 표시됨 |
| 15 | event_impacts.csv | data/event_impacts.csv | 사건과 대상이 존재하고 발표된 피해·공간 노출·분석 가정을 구분함 |
| 16 | regulations.csv | data/regulations.csv | 관할·문서번호·시행 기간·상태가 있음. 과거 규제 사례를 현재 적용 법률로 단정하지 않음 |
| 17 | response_options.csv | data/response_options.csv | 실행 행동·전제·제약·근거 유형이 있어 기업별 적용 여부를 판단할 수 있음 |
| 18 | sources.csv | data/sources.csv | 발행 주체·제목·원문 URL·자료 유형을 추적할 수 있고 보관 위치가 실제 파일과 맞음 |
| 19 | evidence.csv | data/evidence.csv | 대상 기록과 원문이 존재하고 페이지·절·문단 등 근거 위치가 연결됨 |
| 20 | metric_definitions.csv | data/metric_definitions.csv | 지표 정의·단위·합산 규칙·비교 조건을 통해 다른 집계의 혼합을 막음 |
| 21 | classification_mappings.csv | data/classification_mappings.csv | 코드 체계·개정판·대응 범위가 있음. 데이터가 없으면 코드 필터에 연결을 만들어 내지 않음 |
| 22 | relationship_routes.csv | data/relationship_routes.csv | 해당 기업 거래의 실제 경로 근거가 있을 때만 채움. 빈 자료를 임의 경로로 보충하지 않음 |
| 23 | regulation_scopes.csv | data/regulation_scopes.csv | 품목 코드·개정판·원산지·목적지·예외·기간을 함께 해석함. 없으면 품목별 적용 판정을 제공하지 않음 |
| 24 | document_chunks.jsonl | document_chunks.jsonl | 근거 문구를 원문 ID·버전·위치·해시와 함께 생성함. 원문 전체를 수록했는지 짧은 근거만 수록했는지 명시함 |
| 25 | evaluation_cases.csv | data/evaluation_cases.csv | 입력·기대 기업·필수 근거·기대 결과·금지 주장이 정의돼 있음 |
| 26 | region_industries.csv | data/region_industries.csv | 7개 권역과 13개 산업의 조사 범위·우선순위를 원본 표의 의미대로 보존함 |
| 27 | collection_sources.csv | data/collection_sources.csv | 접근 주소·어댑터·갱신 방식·자격증명 환경변수를 등록함. 수동 채널을 자동 갱신으로 표시하지 않음 |
| 28 | data_dictionary.csv | data/data_dictionary.csv | 실제 테이블·열과 이름·자료형·키·참조·누락 규칙이 일치함 |
| 29 | geographies.geojson | geographies.geojson | WGS84 좌표와 region_id를 보존하고 경계 자료의 발행 주체·버전을 추적할 수 있음 |
| 30 | transport_network.geojson | transport_network.geojson | 공식 선형이 없으면 빈 FeatureCollection을 유지함. 직선을 실제 도로·항로로 표시하지 않음 |
| 31 | event_areas.geojson | event_areas.geojson | 자료가 점인지 면인지 보존함. 사건 영향 범위를 임의 반경으로 확정하지 않음 |
| 32 | source_documents/ | source_documents/ | 원문 파일·수집 응답·근거 요약의 유형을 구분하고 실제 상대 경로·해시를 추적할 수 있음 |
| 33 | company_contexts | runtime/kotra.sqlite → company_contexts; db/migrations/001_initial.sql | 기업 조건의 입력 근거·버전을 보존하고 알려지지 않은 재고·납품 물량을 생성하지 않음 |
| 34 | watchlists | runtime/kotra.sqlite → watchlists; db/migrations/001_initial.sql | 유효한 관심 대상만 등록하고 저장 후 다시 조회할 수 있음 |
| 35 | alerts | runtime/kotra.sqlite → alerts; db/migrations/001_initial.sql | 과거·종료·만료 사건을 신규 진행 위험으로 만들지 않으며 읽음·보류·종료 상태가 유지됨 |
| 36 | analysis_runs | runtime/kotra.sqlite → analysis_runs; db/migrations/001_initial.sql | 입력·원문·모델·프롬프트·결과 버전을 보존하고 실패를 성공 분석으로 저장하지 않음 |
| 37 | review_history | runtime/kotra.sqlite → review_history; db/migrations/001_initial.sql | 검토한 분석·보고서 버전과 결정·이유를 보존함 |
| 38 | reports | runtime/kotra.sqlite → reports; db/migrations/001_initial.sql | 분석과 기업이 일치하고 저장·재열기·수정·검토·내보내기가 가능함. 수정 시 승인이 해제됨 |
| 39 | ingestion_runs | runtime/kotra.sqlite → ingestion_runs; db/migrations/001_initial.sql | 성공·실패·추가·수정·거절 수를 남김. 실패를 새 사건 없음으로 해석하지 않음 |
| 40 | record_versions | runtime/kotra.sqlite → record_versions; db/migrations/001_initial.sql | 변경 전후 내용을 당시 버전으로 다시 조회할 수 있음 |
| 41 | users_roles | runtime/kotra.sqlite → users_roles; db/migrations/001_initial.sql | 다중 사용자 기능을 제공할 때 계정 인증·권한·자료 분리가 실제로 적용됨. 테이블만 있으면 다중 사용자 완료로 간주하지 않음 |
| 42 | db/migrations/ | db/migrations/ | 새 DB에서 순서대로 생성되고 외래키·고유키·좌표·구간 순번 제약을 적용함 |
| 43 | ingest/ | ingest/ | CSV를 자료형에 맞게 적재하고 참조 오류 시 반영을 취소함. 수집 실패·중복·재시도 상태를 보존함 |
| 44 | api/ | api/ | 입력 검증 후 조회·분석·수정·검토·보고서를 처리하고 오류를 정상 결과와 구분함 |
| 45 | web/ | web/ | 지역·산업·기업·사건·지도·근거·분석·보고서를 탐색하고 빈 결과·실패·자료 범위를 표시함 |
| 46 | prompts/ | prompts/ | 조회된 자료만 사용하고 사실·가정·대응안을 구분하도록 지시함 |
| 47 | schemas/ | schemas/ | 자료 및 AI 출력의 필수 항목·자료형·ID·근거 연결을 코드에서 검증함 |
| 48 | risk_rules.yaml | risk_rules.yaml | 실제 피해·노출·추론을 구분하고 우선순위·만료 근거를 명시함 |
| 49 | search_index/ | search_index/ | 자료 변경 뒤 다시 생성할 수 있고 근거 문구에서 원문으로 이동할 수 있음 |
| 50 | tests/ | tests/ | 정상 시연과 함께 잘못된 참조·허위 근거·승인 후 수정·과거 사건·중복 적재를 검사함 |
| 51 | .env.example | .env.example | 사용자가 채울 설정 이름과 기본 실행 방식이 있고 실제 키가 포함되지 않음 |
| 52 | dependency_manifest_and_lockfile | requirements.txt; requirements.lock.json; docs/RUNTIME.md | 실행 환경과 외부 의존성 유무를 명시하고 다른 환경에서 설치·실행을 재현할 수 있음 |
| 53 | README.md | README.md | 압축 해제 후 설치·초기화·검증·서버 실행·시연 순서와 실제 제공 범위를 알 수 있음 |
| 54 | report_templates/ | report_templates/ | 보고서의 기업·분석·근거·가정·대응·상태·버전을 표시하고 한글·링크를 내보낼 수 있음 |

## 전체 흐름의 수용 기준

1. CSV 적재 → DB 검증 → 검색 인덱스 생성 → 서버 실행이 안내된 순서대로 완료됨
2. 기업·사건을 선택하고 관계·시설·근거를 열 수 있음
3. 근거 미리보기와 실제 생성형 AI 호출 여부가 화면과 보고서에서 구분됨
4. 실제 생성형 AI를 사용할 때만 별도 API 설정을 요구하고, 설정 실패를 정상 분석으로 바꾸지 않음
5. 분석 결과에 존재하지 않는 기록·근거 ID가 들어오면 저장을 거절함
6. 보고서를 저장하고 수정·검토한 뒤 새로고침해도 해당 버전과 상태를 유지함
7. 승인된 보고서를 수정하면 초안 상태로 돌아가고 이전 검토 이력이 남음
8. 원문 개정 또는 CSV 재적재 이후에도 과거 분석에 쓰인 자료를 다시 볼 수 있음
9. 실제 법률 적용 판정·실제 거래 경로·다중 사용자 인증·실시간 수집은 구현·연결·검증 범위를 구체적으로 표시함
10. KOTRA 사용자 피드백과 운영 배포 검증은 실제 참여와 실행이 끝난 뒤 별도로 기록함

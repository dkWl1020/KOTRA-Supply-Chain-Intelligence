# 데이터 구조

CSV는 첫 적재와 데이터 교환에 사용하고, 실제 분석·검토·보고서·알림은 SQLite에 저장한다. 테이블과 열의 정의는 `schemas/datasets.json`, 열별 설명은 `data/data_dictionary.csv`, 생성 SQL은 `db/migrations/001_initial.sql`에 있다.

## 자료 연결

지역과 산업 → 기업·시설·품목 → 활동·통계·사업·거래 → 사건·영향·대응 → 분석·검토·보고서 순서로 연결한다. 원문과 근거는 각 단계의 사실에 붙는다.

| 구분 | 테이블 | 한 행의 의미 |
| --- | --- | --- |
| 조사 범위 | regions, region_memberships, industries, region_industries | 지역·산업 및 포함 관계 |
| 기업과 기능 | companies, facilities, products, activities | 법인·실제 거점·품목·기업의 역할 |
| 수치와 사업 | metric_definitions, statistics, projects | 지표 정의, 특정 기간의 관측값, 개별 사업 |
| 공급과 운송 | relationships, routes, route_segments, relationship_routes | 기업 사이의 관계, 경로, 경로의 구간, 입증된 거래·경로 연결 |
| 위험과 대응 | risk_profiles, events, event_impacts, regulations, regulation_scopes, response_options | 구조적 위험·사건·영향·조치·조건·대응 선택지 |
| 원문과 수집 | collection_sources, sources, evidence | 수집 설정·발행 자료·특정 기록의 근거 |
| 분류와 평가 | classification_mappings, evaluation_cases | 분류 코드와의 대응, 기대 결과와 금지 주장 |
| 운영 기록 | company_contexts, watchlists, alerts, analysis_runs, review_history, reports, ingestion_runs, record_versions, users_roles | 사용 중 생성되는 조건·알림·작업·검토·보고서·이력 |

## 키와 참조

- 대부분의 테이블: 첫 ID 열을 기본키로 사용
- region_industries: `(region_id, industry_id)` 복합 기본키
- record_versions: `(record_type, record_id, version)` 복합 기본키
- route_segments: 같은 경로에서 `sequence`가 중복되지 않도록 제한
- alerts: `dedupe_key`를 고유하게 유지
- 시설의 운영사와 소유사, 거래의 출발 기업과 도착 기업을 별도 열로 보존
- evidence와 event_impacts 등의 `record_type/target_type`은 테이블 이름, `record_id/target_id`는 해당 행의 ID를 사용
- `object_registry` 뷰는 단일 기본키를 갖는 테이블의 대상을 모아 제공한다. 다형 참조는 적재기·서버에서 유효성을 검사한다. 복합키 대상은 문자열을 임의로 합쳐 연결하지 않는다

외래키는 트랜잭션 종료 시 검사한다. 이 때문에 한 번의 자료 적재 안에서는 자기 참조·상호 참조를 처리할 수 있다. 기존 DB에 일부 파일만 넣을 때도 참조 대상이 있어야 한다. 모든 DB 연결에서 `PRAGMA foreign_keys=ON`을 사용한다.

## 누락과 수치

- CSV 빈칸: SQL `NULL`. 숫자 0은 실제 값으로 보존
- 코드·FIPS: 앞자리 0을 보존하는 문자열
- 날짜: 원문에 연도만 있으면 연도만 기록. 임의로 월·일을 채우지 않음
- 수치: `value`, `unit`, `value_type`, `value_status`, `period`, `scope_note`를 함께 해석
- 범위 수치: lower_bound와 upper_bound를 사용하고, 대표값이 없으면 value는 빈칸
- 다른 기간·산업 범위·소유 범위·단위의 통계는 합산하거나 증감률을 계산하지 않음
- currency, price_basis, base_year, adjustment: 통화·물가 기준·계절조정의 차이를 보존
- source_id와 evidence: 발표된 수치와 이를 뒷받침한 문장·표를 함께 조회할 수 있게 연결
- latitude/longitude: WGS84 십진수 좌표. 도시 중심을 시설 주소로 표시하지 않음

## 사실과 해석

`record_basis`, `assessment_basis`, `support_type`에 실제 발표·공간 노출·분석 가정을 구분해 기록한다. 거래가 알려진 기업이라도 실제 납품 공장이나 항만이 공개되지 않았다면 시설·경로 연결을 비워 둔다. `is_demo`는 가상 데이터, `is_replay`는 과거 사건 재연을 나타낸다. 둘은 다른 의미다.

## 운영과 이력

- sources.version: 원문 개정판 또는 수집본 식별자
- record_versions: 데이터 기록의 버전 이력. 숫자 버전은 같은 대상 안에서 증가
- analysis_runs: 사용한 원문·입력 버전·모델·프롬프트와 결과를 저장
- review_history: 검토자 결정과 이유를 별도 기록
- reports: 보고서 내용을 버전별로 보존. 수정본은 검토 상태를 다시 부여
- alerts의 읽음·보류·종료: 사용자 처리 상태. 사건 종료나 위험 해소로 해석하지 않음

JSON 배열·객체는 SQLite `TEXT` 열에 저장한다. 데이터 사전에 `format=json`으로 표시된 열의 문법과 내부 ID는 서버에서 검증한다. 다중 사용자 인증, 정밀한 공간 연산, 품목별 규제 판정은 실제 구현 범위와 수집된 자료에 맞춰 확장한다.

## 구조 변경

기존 마이그레이션을 수정해 운영 DB를 덮어쓰기보다 새 번호의 SQL 마이그레이션을 추가한다. 열 이름·자료형·허용값이 바뀌면 datasets.json, data_dictionary.csv, 적재기, API 입력 검증을 함께 바꾼다. 적재 전 검사와 외래키 검사를 통과한 자료만 운영 DB에 반영한다.

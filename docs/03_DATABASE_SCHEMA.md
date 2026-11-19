# 03 데이터베이스 스키마 계약
## 기준
SQLite, `PRAGMA foreign_keys=ON`, WAL, migrations 순차 적용, UTC ISO-8601. **테이블 수를 35로 고정하지 않는다.** 다음은 논리 스키마이며 Phase 0에서 실제 SQL DDL과 컬럼 사전으로 확정한다.
## 핵심 도메인(원본 유지)
- 공간: `regions(id PK, code UNIQUE, name_ko, name_en, parent_id FK, region_type, is_benchmark)`, `geographies(id PK, region_id FK, fips UNIQUE, geojson_path, geom_sha256)`, `industries(id PK, code UNIQUE, name_ko, name_en)`.
- 기업: `companies(id PK, canonical_name, country_code, website, verification_status)`, `company_regions(company_id FK, region_id FK, role, PRIMARY KEY(company_id,region_id,role))`, `facilities(id PK, company_id FK NULL, region_id FK, facility_type, latitude NULL, longitude NULL, coordinate_source_id FK NULL)`. 좌표 검증 없이 임의 입력 금지.
- 품목·관계: `products(id PK, name, category)`, `product_hs_codes(product_id FK, hs_code, hs_version, PRIMARY KEY(product_id,hs_code,hs_version))`, `supply_edges(id PK, from_company_id FK, to_company_id FK, relationship_type, tier, confidence, validation_status, valid_from, valid_to)`, `logistics_corridors(id PK, name, mode, source_id FK NULL)`.
- 위험·규제: `events(id PK, event_thread_id, region_id FK, industry_id FK NULL, severity, started_at, ended_at, is_replay, summary)`, `event_impacts(id PK, event_id FK, entity_type, entity_id, impact_type, evidence_id FK NULL)`, `event_timeline(id PK, event_id FK, happened_at, description)`, `regulations(id PK, title, announced_date, effective_date, source_id FK)`, `regulation_impacts`, `tariff_schedules`.
- EWS: `ews_status(id PK, entity_type, entity_id, level, score NULL, confidence, basis, updated_at)`, `ews_history`, `watchlist_items`, `watchlist_reminders`.
- 통계: `trade_stats`, `macro_indicators`, `commodity_prices`, `port_metrics`에는 `region_id`, `metric_id`, `period_start`, `period_end`, `aggregation_basis`, `value`, `unit`, `currency`, `source_id`, `validation_status`를 일관 적용. monthly/cumulative/annual/point_in_time 혼합 집계 금지.
- 근거: `source_documents`, `evidence`, `entity_evidence_map`, `ingestion_runs`, `search_chunks`; FTS5 가상테이블은 별도 생성.
- 분석·보고: `analysis_runs`, `reports`, `report_reviews`, `record_versions`, `users_roles`.
## 확장 테이블
`raw_documents(id PK, source_url, raw_path, sha256 UNIQUE, retrieved_at, license_note, batch_id)`, `raw_records(id PK, raw_document_id FK, payload_json, row_number)`, `collection_jobs(id PK, source_code, schedule, enabled)`, `verification_records(id PK, entity_type, entity_id, status, reviewer, checked_at, note)`, `data_quality_flags(id PK, entity_type, entity_id, code, detail)`, `entity_aliases(id PK, entity_type, entity_id, alias, lang)`, `entity_matches(id PK, left_id, right_id, method, decision)`, `import_batches(id PK, filename, sha256, started_at, status)`, `import_errors(id PK, batch_id FK, row_number, error_code, detail)`.
## 감사·신뢰도 공통 규칙
각 주요 엔티티에 `created_at`, `updated_at`, `validation_status`, `source_id` 또는 연결 테이블 적용. `record_versions`는 entity_type/id, revision, before_json, after_json, actor, changed_at를 저장. `source_documents`의 문서 ID와 `evidence`의 발췌 ID를 구분. `reported`와 `verified`는 자동으로 동일시하지 않음.
## 인덱스
회사 정규명·별칭, 시설 region/type, 사건 region/started_at, 통계(metric,region,period,aggregation_basis), 공급망 양방향 탐색용 from/to, 출처 hash, FTS5 검색. 실제 쿼리 계획 `EXPLAIN QUERY PLAN`으로 검증.
## 마이그레이션·시드
`db/migrations/0001_*.sql`부터 순차 적용; 적용 이력 `schema_migrations` 관리. 기준 데이터 import는 idempotent UPSERT. 데이터 삭제·스키마 변경 시 백업과 롤백 계획 작성.
## SQL 구현 검수
Phase 0의 산출물은 실행 가능한 `0001_initial.sql`, `data_dictionary.csv`, FK 검사, 중복 검사, 100k+ 합성 **성능 테스트 데이터** 생성기. 여기 적힌 스키마는 DDL 대체물이 아니므로 SQL 파일 생성 후 문서와 대조한다.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

# KOTRA 미국 서북부 공급망·통상 위험 대응 시스템 — 통합 시스템 및 UI 상세 설계 명세서 (Complete Specification)

## 1. 시스템 비전 및 도메인 분석 범위

### 1.1 추진 배경 및 핵심 목적
본 시스템은 **KOTRA 실리콘밸리 무역관 관할 미국 서북부 권역**의 핵심 산업 클러스터, 주요 기업, 물류 인프라, 통상·규제 환경, 자연재해 및 노사 분규 등 공급망 교란 요인을 통합 수집·추적하여 **한국 진출 기업과 본사 의사결정권자에게 조기경보(EWS) 및 인과관계 기반 대응 전략을 제공**하기 위해 설계되었습니다.

### 1.2 공간적 분석 범위 (7대 우선 권역 + 1개 비교 기준 권역)
관할 구역의 산업·물류 특성을 정밀하게 반영하기 위해 주(State) 단위와 핵심 경제권(Sub-state)을 구분하여 총 **7개 우선 조사 권역**과 **1개 비교 기준 권역**으로 계층화합니다.

| 권역 코드 | 권역명 (한글) | 권역명 (영문) | 설계 구분 및 주요 모니터링 대상 |
| :--- | :--- | :--- | :--- |
| `US-WA` | 워싱턴주 | Washington | 항공우주(Boeing), 클라우드/AI(Microsoft·Amazon), 시애틀·타코마 항만(NWSA), 농수산·임업 |
| `US-OR` | 오리건주 | Oregon | 반도체 R&D·제조 클러스터(Silicon Forest, Intel), 포토닉스·광학, 임산업, 포틀랜드 항만·물류 |
| `US-ID` | 아이다호주 | Idaho | 메모리 반도체(Micron), 핵심광물(코발트·안티모니 등), 감자·낙농 등 농식품 |
| `US-MT` | 몬태나주 | Montana | 광업·핵심광물(백금족·희토류), 석유·가스·전력 에너지, 대륙횡단 철도 물류 회랑 |
| `US-AK` | 알래스카주 | Alaska | 수산업(명태·연어 등), 석유·가스·광물, 앵커리지 국제 항공화물 허브, 북극항로 |
| `US-CA-NORTH` | 북부 캘리포니아 | Northern California | 실리콘밸리 외곽 첨단제조·에너지·농식품·산불 영향권 (베이지역 9개 카운티와 분리 관리) |
| `US-CA-BAY9` | 베이지역 9개 카운티 | San Francisco Bay Area (9 Counties) | AI·ICT·반도체 설계·바이오 클러스터, 오클랜드 항만, 한국 기업 R&D·법인 밀집지 |
| `US-CA` | 캘리포니아주 전체 | California (Statewide Benchmark) | **비교 기준 권역(Benchmark)** — 주 단위 거시통계 대조 전용 (`US-CA-NORTH`·`US-CA-BAY9`와 합산·대입 금지) |

### 1.3 산업적 분석 범위 (13개 표준 산업 분류)
모든 기업, 시설, 품목, 사건, 규제, 지표 데이터는 아래 **13개 표준 산업 코드**로 일관되게 정규화합니다.
1. **반도체** (Semiconductors)
2. **AI·ICT** (AI & Information/Communications Technology)
3. **항공우주** (Aerospace & Defense)
4. **바이오·헬스** (Bio & Healthcare)
5. **포토닉스·광학** (Photonics & Optics)
6. **첨단·일반 제조** (Advanced & General Manufacturing)
7. **석유·가스** (Oil & Gas)
8. **광업·핵심광물** (Mining & Critical Minerals)
9. **전력·재생에너지** (Electric Power & Renewable Energy)
10. **임산업** (Forestry & Wood Products)
11. **농식품** (Agri-Food)
12. **수산** (Fisheries & Seafood)
13. **물류·항만** (Logistics, Ports & Corridors)

### 1.4 핵심 추적 대상 한국 기업 및 가치사슬 구조
* **주요 한국 기업**: 삼성전자(`CO-SAMSUNG`), SK하이닉스(`CO-SKHYNIX`), 대한항공(`CO-KOREANAIR`), 한국항공우주산업(`CO-KAI`) 등 서북부 권역 내 현지 법인·R&D 센터, 핵심 고객사(Boeing, Intel, Micron, NVIDIA, Amazon, Microsoft 등), 원자재·장비·물류 파트너를 보유한 기업.
* **추적 경로**: 한국 기업 $\rightarrow$ 미국 서북부 1·2·3차 거래처 및 투자 거점 $\rightarrow$ 현지 공장·광산·항만·철도·공항 시설 $\rightarrow$ 권역별 재해·파업·통상·규제 이벤트.

---

## 2. 전체 시스템 아키텍처 및 패키지 청사진

### 2.1 핵심 설계 원칙
* **무의존·자립형 포터블 구조 (Zero-Bloat Portable Architecture)**: 외부 상용 DB나 무거운 런타임 없이 Python 표준 라이브러리(`http.server`, `sqlite3`, `json`, `csv`, `hashlib`, `urllib`, `re`)와 내장 SQLite FTS5 엔진만으로 즉시 구동·이관 가능하도록 설계합니다.
* **단일 진실 공급원 (Single Source of Truth)**: 기준 마스터 CSV(`data/*.csv`)와 원문 대조 메모(`source_documents/*.md`)를 적재기(`run.py init`)로 검증·정규화하여 SQLite DB(`runtime/kotra.sqlite`) 및 하이브리드 검색 인덱스(`search_index/`)를 생성합니다.
* **완전한 감사 추적성 (Full Auditability)**: 레코드 수정, EWS 등급 변경, 보고서 편집·승인 이력은 모두 버전 테이블(`record_versions`)과 검토 이력(`report_reviews`)에 스냅샷으로 보존됩니다.

### 2.2 표준 디렉터리 구조 (`KOTRA_final/`)
```text
KOTRA_final/
├── run.py                  # 통합 CLI 진입점 (init, validate, index, serve, collect-usgs)
├── api/                    # 백엔드 HTTP 서버, 라우터, 비즈니스 로직, SQLite 저장소
│   ├── server.py           # 20개 REST API 엔드포인트 라우터 및 정적 웹 서빙
│   ├── store.py            # SQLite 트랜잭션, 버전 이력, FTS5/Unicode 하이브리드 검색
│   └── services.py         # 도메인 분석·EWS·스크랩 병합·보고서·가드레일 서비스 엔진
├── web/                    # 프론트엔드 SPA (7대 화면, SVG 지도·네트워크, 모달, 보고서 에디터)
│   ├── index.html          # 단일 페이지 앱 골격 및 모달·템플릿 컨테이너
│   ├── styles.css          # 대시보드 그리드, 상태 배지, SVG 그래프, 인쇄 스타일시트
│   └── app.js              # 상태 관리, API 클라이언트, 7개 탭 렌더러, SVG 시각화 엔진
├── data/                   # 27종 기준 마스터 CSV 및 데이터 사전(data_dictionary.csv)
├── db/
│   └── migrations/         # 35개 테이블 및 FTS5 가상 테이블 DDL 정의 SQL
├── ingest/                 # CSV 적재기, SHA-256/외래키 검증기, 외부 피드·API 수집기
├── source_documents/       # 102건 원문 대조 메모(.md) 및 SHA-256 무결성 해시 원천 자료
├── report_templates/       # HTML 보고서 템플릿 3종 (report.html, ews_monthly.html, kakao_insight.html)
├── scripts/                # GeoJSON 경계 수집(fetch_geographies.py) 및 보조 유틸리티
├── docs/                   # 검수 기준(ACCEPTANCE.md), 빌드 순서, 검증 결과 문서
├── examples/               # 실제 사례 기반 출력 예시 (korean_air_report.html 등)
├── tests/                  # 단위·무결성 테스트(test_runtime.py) 및 E2E 테스트(test_e2e_browser.py)
├── runtime/                # 런타임 SQLite DB (kotra.sqlite)
└── search_index/           # 청크 직렬화(document_chunks.jsonl) 및 매니페스트
```

---

## 3. 전체 기사 및 외부 데이터 수집 파이프라인 설계

### 3.1 다채널 수집원 아키텍처 (15개 수집 채널)
시스템은 공공 통계·재난 피드·통상 DB의 **자동 수집 파이프라인**과 무역관 현장 모니터링·언론 기사의 **수동 스크랩 파이프라인**을 결합하여 운영합니다. (`collection_sources.csv` 기준 15개 채널 관리)

| 채널 구분 | 대상 기관 / 매체 | 수집 방식 | 수집 주기 | 주요 적재 테이블 |
| :--- | :--- | :--- | :--- | :--- |
| **기상·재난·지질 (3종)** | NWS(국립기상청), USGS(지질조사국 지진·수문), FEMA(재난관리청) | REST/GeoJSON 자동 수집 (`urllib` + 표준 `User-Agent`) | 일 1회 / 특보 시 | `events`, `event_impacts` |
| **법령·관세·공시 (2종)** | Federal Register(연방관보), SEC EDGAR(10-K/8-K 공시) | API/피드 자동 수집 및 키워드 필터링 | 일 1회 | `regulations`, `companies`, `evidence` |
| **거시·고용·무역 (4종)** | U.S. Census Bureau, BLS QCEW, BEA 지역 GDP, USDA 농무부 | 분기·월간 통계 API / CSV 배치 적재 | 월간 / 분기별 | `trade_stats`, `macro_indicators` |
| **에너지·수산·항만 (3종)** | EIA(에너지정보청), NOAA(해양대기청), NWSA(북서부항만동맹) | 통계 피드 및 항만 물동량 스냅샷 적재 | 월간 | `macro_indicators`, `facilities` |
| **언론·업계·현장 (3종)** | 주요 경제지(Reuters, Bloomberg, Seattle Times), 전문지, 무역관 현장 제보 | 담당자 수동 스크랩 입력(`POST /api/scraps`) 및 원문 메모 등록 | 수시 (실시간) | `events`, `evidence`, `source_documents` |

### 3.2 기사 스크랩 등록 및 동일 사건 스레드 자동 병합 (`create_scrap`)
담당자가 새로운 뉴스 기사나 현장 동향을 등록할 때 사건이 파편화되지 않도록 **사건 스레드 병합(Event Thread Merging)** 알고리즘을 수행합니다.

1. **서지 메타데이터 자동 검증 (`missing_metadata_fields`)**:
   * 입력 페이로드에서 `title`, `url`, `publisher`, `published_at`, `region_id`, `industry_id`, `excerpt`, `evidence_tier`를 검사합니다.
   * 언론사명(`publisher`), 발행일(`published_at`), 원문 링크(`url`) 등 필수 서지 항목이 누락된 경우 저장은 허용하되 응답 객체의 `missing_metadata_fields` 배열에 누락 필드명을 기록하고 UI에 보완 배지를 표시합니다.
2. **동일 사건 스레드 탐색 및 자동 병합 (`event_thread_id`)**:
   * 입력값에 `event_thread_id`가 명시되었거나, 동일 권역(`region_id`)·산업(`industry_id`) 내 최근 30일 이내 활성 사건 중 제목·핵심 키워드 유사도가 임계치를 넘는 기존 `events` 레코드가 존재할 경우 신규 사건을 중복 생성하지 않습니다.
   * 대신 기존 사건의 `events.summary` 타임라인에 후속 경과를 누적 병합하고, 신규 기사 발췌문(`evidence`)과 원문 출처(`source_documents`)를 해당 `event_id`에 하위 근거로 연결합니다.
   * 기존 사건의 심각도가 상승한 경우(`severity` 상향) 연관된 `ews_status` 검토 알림을 자동 생성합니다.

### 3.3 중복 제거, 장애 격리 및 원문 무결성 검증
* **중복 방지 (Idempotency)**: `source_documents` 적재 시 원문 본문 또는 URL 정규화 문자열의 `SHA-256` 해시를 계산하여 동일 해시가 이미 존재하면 중복 적재를 건너뛰고 기존 `source_id`를 재사용합니다.
* **장애 격리 (Fault Isolation via `ingestion_runs`)**:
  * 외부 API 호출 시 HTTP 403/429/5xx 오류, 네트워크 타임아웃, API 키 미설정 등이 발생하더라도 기존 DB의 정상 데이터를 삭제하거나 '사건 0건'으로 덮어쓰지 않습니다.
  * 모든 수집 배치는 `ingestion_runs` 테이블에 `run_id`, `source_code`, `started_at`, `finished_at`, `status`(`success` | `partial` | `failed`), `records_inserted`, `error_message`를 기록하며 트랜잭션 단위로 롤백·격리됩니다.
* **원문 대조 해시 검증 (`run.py validate`)**: `source_documents/` 디렉터리의 102개 원문 대조 메모(`.md`)의 실제 파일 `SHA-256` 해시와 `data/source_documents.csv`에 기록된 해시값을 전수 대조하여 위·변조 및 누락을 0건으로 통제합니다.

---

## 4. 관계형 데이터베이스(35개 테이블) 및 하이브리드 검색 설계

### 4.1 35개 SQLite 테이블 도메인별 구조
`db/migrations/`의 DDL 스크립트는 27종 기준 CSV와 런타임 상태 데이터를 수용하기 위해 총 **35개 테이블**로 정규화됩니다.

| 도메인 영역 | 테이블 목록 (총 35개) | 핵심 설계 역할 및 제약조건 |
| :--- | :--- | :--- |
| **1. 공간·산업·지표 기준 (5개)** | `regions`, `geographies`, `industries`, `metric_definitions`, `collection_sources` | 7+1 권역 계층(`parent_region_id`), GeoJSON 경계 메타, 13개 산업 코드, 지표 단위·집계 기준, 15개 수집원 정의 |
| **2. 기업·거점·공급망 (7개)** | `companies`, `company_regions`, `facilities`, `products`, `product_hs_codes`, `supply_edges`, `logistics_corridors` | 한국/미국 기업 마스터, 권역별 활동 역할, 검증 좌표 기반 시설(`port`, `rail_terminal`, `airport`, `fab`, `mine`), HS4/HS6 품목, 방향성 공급망 엣지(`relationship_type`, `tier`) |
| **3. 사건·위험·규제 (6개)** | `events`, `event_impacts`, `event_timeline`, `regulations`, `regulation_impacts`, `tariff_schedules` | 재해·파업·통상 사건(`is_replay`, `event_thread_id`), 권역·산업·기업별 파급효과, 법령·관세 발표일(`announced_date`)·시행일(`effective_date`) |
| **4. 조기경보·알림 (4개)** | `ews_status`, `ews_history`, `watchlist_items`, `watchlist_reminders` | 권역×산업/품목 EWS 4단계 등급(`alert`, `caution`, `watch`, `normal`), `escalate_next_month`, `remind_at`, 규제 D-Day 알림 |
| **5. 통계·정량 지표 (4개)** | `trade_stats`, `macro_indicators`, `commodity_prices`, `port_metrics` | 교역액·물동량·고용·에너지 통계, `aggregation_basis` 4종(`monthly`, `cumulative`, `annual`, `point_in_time`), 환율 주석(`fx_impact_note`) |
| **6. 근거·원문·수집이력 (5개)** | `source_documents`, `evidence`, `entity_evidence_map`, `ingestion_runs`, `search_chunks` | 원문 경로 및 `sha256`, 발췌문(`excerpt`), 근거 신뢰도(`evidence_tier` 1\~4등급), 엔티티 다대다 매핑, 배치 수집 로그, 검색 청크 |
| **7. 분석·보고·거버넌스 (4개)** | `analysis_runs`, `reports`, `report_reviews`, `record_versions` (+ `users_roles`) | 5단계 인과분석 결과 스냅샷, 편집 가능한 보고서 초안, 승인/수정요청/반려 이력, 전 테이블 감사 버전 이력, 사용자 역할 |

### 4.2 근거 신뢰도 4등급 분류 체계
* **1등급 (공식 통계·법령·공시)**: 연방·주 정부 기관(Census, BEA, BLS, EIA, USGS, Federal Register), 상장사 SEC 공시.
* **2등급 (기관·산업협회 보고서)**: KOTRA 해외시장뉴스, 반도체·항공·항만 협회 공식 발표, 공공 항만청(NWSA 등) 리포트.
* **3등급 (주요 언론·전문지 보도)**: 로이터, 블룸버그, 시애틀타임스 등 복수 교차 검증된 주요 경제·산업 매체.
* **4등급 (현장 스크랩·담당자 제보)**: 무역관 현장 모니터링, 기업 인터뷰, 미확인 초기 속보(`missing_metadata_fields` 점검 대상).

### 4.3 하이브리드 검색 인덱스 (`search_index` + FTS5)
* `run.py index` 실행 시 `evidence`, `events`, `regulations`, `source_documents`의 텍스트를 청킹하여 `search_index/document_chunks.jsonl`에 직렬화하고 SQLite `FTS5` 가상 테이블(`search_chunks_fts`)을 구축합니다.
* 영문 형태소 매칭은 `FTS5`를 우선 사용하고, 한국어 조사·부분일치 및 한·영 기업명 교차 조회(`보잉` $\leftrightarrow$ `Boeing`, `삼성` $\leftrightarrow$ `Samsung`, `하이닉스` $\leftrightarrow$ `SK hynix`, `대한항공` $\leftrightarrow$ `Korean Air`, `마이크론` $\leftrightarrow$ `Micron`, `인텔` $\leftrightarrow$ `Intel`)를 위해 Unicode 부분일치 및 동의어 확장 쿼리를 결합합니다.

---

## 5. 백엔드 비즈니스 엔진 및 20개 REST API 계약

### 5.1 핵심 분석 알고리즘 3종
1. **품목 8대 필러 브리프 (`get_product_brief`)**:
   * 선택 품목을 **①개요·HS코드 ②서북부 생산·교역 ③밸류체인·주요기업 ④한국 기업 연관성 ⑤가격·수급 동향 ⑥물류·통관 병목 ⑦규제·보조금 환경 ⑧종합 리스크 및 미국 현지 대체 공급처(`get_alternatives`)**의 8개 필러로 구조화합니다.
   * **가격·수급 분기 로직**: `product_category == 'raw_material'`(원자재)인 경우 공개 국제 시세를 표기하고, 소재·부품·완제품(`component`, `finished`)인 경우 비공개 B2B 단가를 추정하지 않고 설비투자(CapEx)·고용·교역량 프록시 지표를 제시합니다.
2. **3-Hop 공급망 역추적(BFS) 및 5단계 인과분석 (`analyze`)**:
   * 한국 기업 노드에서 출발하여 `supply_edges`를 따라 최대 3단계(1-Hop 직접 거래처 $\rightarrow$ 2-Hop 하위 부품·물류 거점 $\rightarrow$ 3-Hop 원재료·인프라)까지 너비 우선 탐색(BFS)을 수행합니다.
   * 탐색된 경로와 대상 사건/규제를 결합하여 **①직접 영향 $\rightarrow$ ②간접·경합 효과 $\rightarrow$ ③근거 4등급 분류 $\rightarrow$ ④데이터 가드레일 주석 $\rightarrow$ ⑤역할별(본사·현지법인·무역관) 대응안**의 5단계 구조화 보고서를 생성합니다.
3. **EWS 4단계 트리아지 및 D-Day 리마인더 (`get_ews`, `get_reminders`)**:
   * `alert`(경보) $\rightarrow$ `caution`(주의) $\rightarrow$ `watch`(관찰) $\rightarrow$ `normal`(정상) 순으로 우선순위를 정렬하며, 규제 발표일과 시행일 간 잔여 일수(D-Day) 및 `escalate_next_month` 플래그를 자동 계산합니다.

### 5.2 주요 REST API 엔드포인트 명세 (20개 라우트)

| 그룹 | HTTP 메서드 및 경로 | 주요 기능 및 요청/응답 계약 |
| :--- | :--- | :--- |
| **기준·현황** | `GET /api/catalog` | 7+1 권역, 13개 산업, 품목, 한국 기업, 지표 정의 마스터 카탈로그 반환 |
| | `GET /api/overview` | 상단 KPI 요약, EWS 긴급 트리아지 큐, 7대 권역 요약, 캘리포니아 분리 주석 반환 |
| | `GET /api/reminders` | 관심목록 리마인더 + 규제 시행 D-Day + 프로젝트 목표가동일 큐 반환 |
| **기업·시설** | `GET /api/companies` | 권역·산업·국가별 기업 목록 조회 (`?region_id=&industry_id=&q=`) |
| | `GET /api/facilities` | 검증된 위·경도 좌표를 보유한 시설 마커 목록 반환 (지도 렌더링용) |
| | `GET /api/network` | 기업 간 방향성 관계 그래프(`nodes`, `edges`, `relationship_type`) 및 3-Hop 경로 반환 |
| **품목·물류** | `GET /api/products/{product_id}/brief` | 품목 8대 필러 브리프 및 시세/프록시 분기 데이터 반환 |
| | `GET /api/alternatives` | HS4·산업·권역 기준 미국 현지 대체 공급처 매트릭스 반환 |
| | `GET /api/logistics` | 해상 항만(`port`, `port_terminal`), 철도(`rail_terminal`), 공항(`airport`) 회랑 및 물동량 지표 |
| **통계·스크랩** | `GET /api/trade-stats` | 집계 기준(`aggregation_basis`) 및 권역·품목별 교역·거시 지표 조회 |
| | `POST /api/trade-stats` | 신규 무역통계 등록 (`aggregation_basis` 4종 필수 검증 및 `fx_impact_note` 환율 주석 저장) |
| | `POST /api/scraps` | 기사·현장 스크랩 등록, `event_thread_id` 자동 병합, `missing_metadata_fields` 반환 |
| **사건·EWS** | `GET /api/events` | 진행 중 사건(`is_replay=0`)과 과거 재연 사례(`is_replay=1`) 분리 조회 |
| | `GET /api/ews` / `POST /api/ews` | 권역×산업/품목 EWS 등급 조회 및 등급(`alert`~`normal`)·익월 상향·노트 갱신 |
| **분석·보고** | `POST /api/analyze` | 대상 기업·사건·규제 입력 시 3-Hop 역추적 + 5단계 인과분석 실행 및 초안 저장 |
| | `PUT /api/reports/{report_id}` | 보고서 본문 편집 저장 (수정 시 기존 `approved` 상태를 자동으로 `needs_review`로 전환) |
| | `POST /api/reports/{report_id}/review` | 책임자 검토 상태(`approve` | `request_changes` | `reject`) 및 검토 의견 기록 |
| | `GET /api/reports/{report_id}/export` | 3종 템플릿(`desk_briefing`, `ews_monthly`, `kakao_insight`) HTML 생성 및 내부 ID 정제 출력 |
| **근거·상세** | `GET /api/evidence/search` | FTS5 + Unicode + 한·영 기업명 동의어 확장 원문 근거 검색 |
| | `GET /api/detail/{entity_type}/{id}` | 임의 엔티티 상세 속성 + 연결된 근거 목록(`evidence`) + 원문 메타 반환 |

---

## 6. 프론트엔드 UI/UX 및 컴포넌트 상세 구현 명세 (`web/`)

프론트엔드(`web/index.html`, `web/styles.css`, `web/app.js`)는 단일 페이지 애플리케이션(SPA)으로 구성되며, 상단 글로벌 바, **7개 메인 화면 탭**, **2종의 SVG 시각화 엔진**, **상세 드릴다운 모달**, 그리고 **보고서 에디터·내보내기 워크플로우**를 제공합니다.

### 6.1 글로벌 레이아웃 및 상단 툴바 (`index.html`)
* **상단 헤더 바**: 시스템 타이틀, 전역 권역 선택기(7대 우선 권역 + 캘리포니아 비교군), 전역 산업 필터(13개 산업), 빠른 실행 버튼(**`+ 기사 스크랩 등록`**, **`+ 무역통계 입력`**).
* **상시 가드레일 알림 배너**: `US-CA-NORTH` 또는 `US-CA-BAY9` 선택 시 *"북부 캘리포니아 및 베이지역 9개 카운티 지표는 캘리포니아 주 전체(`US-CA`) 통계와 분리 집계됩니다"* 안내 배너를 상단에 고정 표출.

### 6.2 7개 메인 화면 구성 및 테이블 매핑 (`web/app.js`)

| 탭 번호 및 화면명 | 상단 KPI 카드 구성 | 필터 툴바 | 메인 뷰 및 데이터 테이블 컬럼 매핑 (`cols` / `names`) |
| :--- | :--- | :--- | :--- |
| **1. 기업과 시설** | 추적 한국 기업 수, 현지 파트너사 수, 검증 좌표 시설 수, 주요 산업 클러스터 수 | 권역, 산업, 기업유형(한국/미국/글로벌), 검색어 | **상단 2분할 시각화**: 좌측 **시설 위치 지도(`loadMap`)** + 우측 **기업 관계 네트워크(`renderNetwork`)**<br>**하단 테이블**: 기업명(`company_name`), 역할(`role`), 권역(`region_name`), 산업(`industry_name`), 주요 시설(`facility_name`), 시설유형(`facility_type`), 근거건수(`evidence_count`) |
| **2. 지역과 산업** | 7대 권역별 EWS 경보 건수, 핵심 산업 클러스터 수, 주요 거점 비율 | 권역 선택 카드(7+1), 13개 산업 매트릭스 셀 클릭 | **권역×산업 교차 히트맵 매트릭스** 및 선택 셀의 **품목 8대 필러 브리프** 아코디언 패널 + 미국 현지 대체 공급처 비교 테이블 |
| **3. 수치 데이터** | 최신 교역액(집계기준 명시), 항만 TEU 물동량, 고용·투자 프록시 건수 | 지표유형(무역/거시/물류), 집계기준(`monthly`·`cumulative`·`annual`), 품목 | **집계기준 분리 차트** + **환율 착시 주석(`fx_impact_note`) 배지**<br>**테이블**: 지표명(`metric_name`), 권역(`region_name`), 기준기간(`period`), 집계기준(`aggregation_basis`), 수치(`value`), 단위(`unit`), 환율주석(`fx_impact_note`) |
| **4. 사건과 위험** | 활성 경보(`alert`), 주의(`caution`), 관찰(`watch`), 과거 재연 시나리오(`is_replay=1`) 수 | 상태 탭(**진행 중 사건** vs **과거 재연 사례** 분리), EWS 등급, 권역 | **EWS 4단계 트리아지 관리 테이블** (인라인 등급 변경 드롭다운, `escalate_next_month` 체크박스, 담당자 메모 저장 버튼) + 사건 스레드 타임라인 |
| **5. 분석과 보고서** | 생성된 분석 건수, 검토 대기 보고서, 승인 완료 보고서 | 대상 한국 기업, 대상 사건/규제, 템플릿 유형(3종) | **좌측**: 3-Hop 역추적 조건 설정 & **`분석 실행`** 버튼<br>**우측**: **5단계 인과분석 결과 뷰어** + **보고서 편집기(`editReport`)** + 검토 승인 바 + HTML 내보내기 버튼 |
| **6. 자료와 근거** | 전체 근거 473건, 원문 대조 메모 102건, 근거 등급별(1\~4등급) 분포 | 한·영 통합 검색창, 근거 등급(1\~4등급), 메타데이터 누락 여부 | **원문 근거 검색 결과 리스트**: 발췌문(`excerpt`), 신뢰도 등급 배지(`1등급`~`4등급`), 출처문서명(`source_title`), 발행일(`published_at`), SHA-256 검증 상태 배지 |
| **7. 관심 대상과 알림** | 규제 시행 D-Day 임박 건수, 익월 상향 예약 건수, 관심 품목·기업 수 | D-Day 정렬, 담당자별 필터, 상태별 필터 | **규제 발표→시행 시차 D-Day 카운트다운 카드** + 관심 기업/품목 모니터링 큐 + 리마인더 완료 처리 토글 |

### 6.3 SVG 시각화 컴포넌트 상세 명세

#### A. 시설 위치 지도 (`loadMap`)
* **좌표 렌더링 원칙**: `facilities` 테이블에서 공공 GIS 또는 검증된 도로명 주소로 위·경도(`latitude`, `longitude`)가 확정된 시설만 필터링하여 SVG 좌표계로 투영하고 `<circle>` 마커로 렌더링합니다.
* **환각 방지 제약**: 좌표가 확인되지 않은 시설에는 임의 좌표를 생성하지 않고 별도 *"좌표 미확인 시설 목록"* 배지로만 안내하며, 검증되지 않은 행정 경계선이나 임의의 해상·육상 운송 경로선을 지도 위에 임의 작도하지 않습니다.
* **인터랙션**: 마커 호버 시 시설명·운영사·시설유형 툴팁을 표시하고, 클릭 시 `showDetail('facility', id)` 모달을 호출합니다.

#### B. 기업 관계 네트워크 (`renderNetwork`)
* **방향성 그래프 구조**: 출발 노드(`from_company_id`)에서 도착 노드(`to_company_id`)로 향하는 SVG `<marker>` 방향 화살표로 가치사슬 흐름을 시각화합니다.
* **관계 유형별 엣지 시각 스타일**:
  * **공급·주문 (`supply` / `order`)**: 실선, 파란색(`#2563eb`), 선 두께는 의존도(`dependency_level`)에 비례.
  * **자산 인수·지분 투자 (`acquisition` / `investment`)**: 점선(`stroke-dasharray="5,4"`), 황토색(`#b45309`).
  * **합작·기술 제휴 (`joint_venture` / `partnership`)**: 실선, 청록색(`#0f766e`).
* **노드 시각 구분 및 인터랙션**:
  * 한국 추적 기업(삼성전자, SK하이닉스, 대한항공, KAI 등)은 강조 테두리 노드로 배치하고, 1-Hop·2-Hop·3-Hop 거리에 따라 계층 배치합니다.
  * 특정 노드 클릭 시 연결된 3-Hop 경로만 하이라이트하고 나머지 노드는 투명도(`opacity: 0.2`) 처리하며, 엣지 클릭 시 해당 거래 관계의 원문 근거(`evidence`)를 즉시 조회합니다.

### 6.4 근거 드릴다운 모달 및 보고서 검토·내보내기 워크플로우
1. **행 클릭 상세 모달 (`showDetail` & `renderEvidence`)**:
   * 7개 화면의 어떤 테이블 행이나 지도·네트워크 요소를 클릭하더라도 우측 슬라이드오버/모달(`showDetail`)이 열리며, 상단에 엔티티 핵심 속성(내부 코드 제거 완료 상태)을 표시하고 하단에 `renderEvidence()`가 연결된 1\~4등급 근거 카드와 원문 대조 메모(`source_documents/*.md`) 열람 링크를 렌더링합니다.
2. **보고서 편집 및 승인 자동 해제 워크플로우 (`editReport`)**:
   * `분석 실행` 완료 후 생성된 5단계 인과분석 초안은 보고서 편집기(`editReport`)에서 담당자가 문구를 직접 수정·보완할 수 있습니다.
   * **무결성 통제 규칙**: 이미 책임자 승인을 받은(`review_status == 'approved'`) 보고서라도 담당자가 본문을 1글자라도 수정하여 저장(`PUT /api/reports/{id}`)하는 순간 승인 상태가 자동으로 해제(`needs_review`)되며, `record_versions`에 수정 전·후 스냅샷이 기록됩니다.
3. **3종 템플릿 HTML 내보내기 (`export_report`)**:
   * 검토가 완료된 보고서는 목적에 따라 아래 3종 템플릿 중 하나를 선택해 독립 실행형 HTML 파일로 내보냅니다.
     * **`desk_briefing` (`report_templates/report.html`)**: 무역관 데스크 심층 브리핑 및 5단계 인과분석 정식 보고서.
     * **`ews_monthly` (`report_templates/ews_monthly.html`)**: 월간 조기경보(EWS) 종합 점검 및 차월 중점 관찰 대상 보고서.
     * **`kakao_insight` (`report_templates/kakao_insight.html`)**: 유관기관·기업 담당자 메신저 전파용 핵심 요약 카드형 브리프.
   * 내보내기 직전 `sanitize_internal_ids()` 필터가 실행되어 본문과 표 전체에서 `CO-*`, `FAC-*`, `PRD-*`, `EVD-*`, `SRC-*` 등 내부 식별자를 공식 한글·영문 명칭으로 치환합니다.

---

## 7. 5대 데이터 가드레일 및 환각 방지 설계

시스템 전 계층(DB 검증기, 백엔드 서비스, 프론트엔드 UI, HTML 보고서 출력기)에는 아래 **5대 가드레일**이 강제 적용됩니다.

1. **지리적 집계 분리 원칙**: 북부 캘리포니아(`US-CA-NORTH`)와 베이지역 9개 카운티(`US-CA-BAY9`) 지표에 캘리포니아 주 전체(`US-CA`) 수치를 대입하거나 합산하지 않습니다.
2. **과거 재연 사례(`is_replay = 1`) 분리 원칙**: Boeing 2024년 파업·MAX-9 감항지시, Merbok 폭풍, 옐로스톤 홍수, Dixie 산불 등 과거 사례(`is_replay = 1`)는 현재 진행 중인 활성 EWS 경보(`is_replay = 0`)와 분리하여 스트레스 테스트 시나리오로만 활용합니다.
3. **비공개 B2B 단가·재고 및 임의 GIS 좌표 생성 금지**: 기업 간 비공개 납품 단가·재고는 추정치를 생성하지 않고 CapEx·고용·교역 프록시로 대체하며, 공공 GIS·도로명 주소가 원문 확인된 시설만 지도 좌표를 표기합니다.
4. **무역통계 집계 기준 분리 및 환율 착시 가드레일**: `monthly`·`cumulative`·`annual`·`point_in_time` 기준을 혼용하지 않으며, 달러(`USD`) 명목 증감 시 원/달러 환율 변동 착시 주석(`fx_impact_note`)을 병기합니다.
5. **내부 시스템 코드 비노출 원칙**: 사용자 화면과 HTML 보고서 출력 시 `CO-*`, `FAC-*`, `PRD-*`, `EVD-*`, `SRC-*` 등 내부 DB 식별자가 절대 노출되지 않도록 치환합니다.

---

## 8. CLI 파이프라인, 자동화 검증 및 검수 기준

### 8.1 표준 CLI 운영 명령어 (`run.py`)
* `python3 run.py init`: 35개 테이블 DDL 마이그레이션 적용, 27개 기준 CSV 적재, 도메인 제약조건 검증.
* `python3 run.py validate`: 외래키·복합키 참조 무결성 오류 `0건`, 102개 원문 대조 메모(`source_documents/`)의 `SHA-256` 해시 일치 여부 전수 검사.
* `python3 run.py index`: `search_index/document_chunks.jsonl` 및 SQLite `FTS5` 검색 인덱스 재구축.
* `python3 run.py serve --port 8000`: 백엔드 REST API 및 프론트엔드 SPA 웹 서버 실행.
* `python3 run.py collect-usgs`: USGS 지진·수문 피드 수집 및 `ingestion_runs` 이력 기록.

### 8.2 자동화 테스트 스위트 (`tests/`)
* **단위·무결성 테스트 (`tests/test_runtime.py`, 10개 항목)**: DB 참조 무결성, 7대 권역·8대 필러 브리프, 대체 공급망 매트릭스, EWS 등급 갱신, 동일 사건 스레드 스크랩 병합(`event_thread_id`), 무역통계 집계기준·환율 가드레일, 3-Hop 네트워크 역추적, 물류 회랑 조회, 보고서 3종 템플릿 내보내기 및 내부 코드 비노출 검증.
* **E2E 시나리오 테스트 (`tests/test_e2e_browser.py`, 8개 시나리오)**: 정적 웹 자산(`index.html`, `styles.css`, `app.js`) 및 GeoJSON 피처 무결성, 한·영 교차 근거 검색, 수동 스크랩 등록부터 인과분석·편집·승인·HTML 내보내기까지의 전 주기 왕복 검증.
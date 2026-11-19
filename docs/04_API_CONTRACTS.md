# 04 REST API 계약
## 공통 규칙
`/api/v1` 버전 경로, JSON UTF-8, UTC ISO-8601, `limit` 기본 50 최대 200, `offset` 기본 0, 정렬 allowlist, 검색어 최대 길이 제한. 리스트 응답 `{items:[],page:{limit,offset,total},filters:{}}`; 오류 `{error:{code,message,details,request_id}}`. DB 내부 식별자는 API에서는 사용하되 UI 텍스트·보고서에는 노출 금지. 조회/수정 시 입력 검증, SQL 파라미터 바인딩, 출력 이스케이프.
## 필수 엔드포인트
| Method | Path | 필수 쿼리/본문 | 핵심 응답 |
|---|---|---|---|
| GET | `/catalog` | 없음 | regions, industries, products, metrics |
| GET | `/overview` | region_id?,industry_id?,as_of? | kpis, top_events, industries, data_freshness |
| GET | `/companies` | q?,region_id?,industry_id?,limit?,offset? | 회사 목록 페이지 |
| GET | `/facilities` | bbox?,zoom?,region_id?,type? | marker 또는 cluster, total |
| GET | `/network` | company_id 필수, hops=1..3 | nodes,edges,paths,provenance |
| GET | `/products/{id}/brief` | 없음 | 8 pillars, sources, unknown_fields |
| GET | `/alternatives` | product_id 또는 hs_code | candidates, match_reasons, evidence |
| GET | `/logistics` | region_id?,mode? | corridors, facilities, metrics |
| GET | `/trade-stats` | metric_id?,region_id?,basis?,from?,to? | series,unit,basis,source |
| POST | `/trade-stats` | validated metric payload | id,revision |
| POST | `/scraps` | title, excerpt?, url?, region_id?, industry_id? | id,thread_id,missing_metadata_fields |
| GET | `/events` | is_replay?,region_id?,severity? | events page |
| GET | `/ews` | entity_type?,region_id?,level? | statuses page |
| POST | `/ews` | entity_type,entity_id,level,reason | status,history_id |
| POST | `/analyze` | target_type,target_id,event_id?,engine=`rule` | analysis_id, risk, paths, evidence, warnings |
| GET | `/reports` | status?,limit?,offset? | reports page |
| GET | `/reports/{id}` | 없음 | report document model |
| PUT | `/reports/{id}` | revision,content | new_revision,review_status |
| POST | `/reports/{id}/review` | decision,note | review entry (운영 단계) |
| GET | `/reports/{id}/export` | format=html/pdf/docx | attachment + content type |
| GET | `/evidence/search` | q,filters?,limit?,offset? | snippets,source,status |
| POST | `/search/query` | `{question,filters}` | interpreted_filters,results,limitations |
| GET | `/detail/{type}/{id}` | 없음 | entity, evidence, provenance |
| GET | `/reminders` | due_before?,status? | reminders page |
| POST | `/admin/imports` | CSV upload, dataset_type | batch_id,preview,errors |
| POST | `/admin/imports/{id}/commit` | expected_checksum | counts,status |
| GET | `/admin/ingestion-runs` | status?,source? | runs page |
| GET | `/admin/health` | 없음 | db,index,storage,collection summary |

## 요청/응답 예시 — 분석
요청: `{"target_type":"company","target_id":"CO-EXAMPLE","engine":"rule"}`
응답: `{"analysis_id":"ANL-EXAMPLE","engine":"rule","risk":{"score":null,"level":"watch","confidence":"low","is_heuristic":true},"paths":[],"evidence_ids":[],"recommendations":[],"warnings":["Insufficient verified evidence"]}`. 모든 EXAMPLE 값은 계약 예시이며 실데이터 아님.
## 동작·오류 계약
- `400` invalid input, `404` unknown entity, `409` revision conflict, `413` oversized upload, `422` semantic validation, `429` rate limit(운영), `500` internal error, `503` unavailable dependency.
- 결과 0건은 200 + 빈 배열과 이유 표시. 수집 실패를 0건으로 덮어쓰지 않음.
- 수정은 revision 낙관적 잠금, DB 트랜잭션, 감사 로그 기록. 승인된 보고서 수정 시 `needs_review` 전환.
- `/admin/*`는 초기 loopback에서만 활성, 외부 공개 시 인증/RBAC 전 필수 차단.
- 브라우저와 서버는 이 계약을 테스트 fixture로 공유; endpoint 추가 시 이 문서와 테스트 동시 변경.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

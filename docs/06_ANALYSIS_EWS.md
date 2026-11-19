# 06 분석 및 EWS 엔진
## 책임 분리
`GraphExplorer`는 확정된 방향성 관계로 1–3 Hop BFS 수행; `RiskEngine`은 사건/통계/규제·근거를 결합; `AlternativeFinder`는 HS 코드·산업·시설·역량 후보를 검색; `AnalysisRenderer`는 결과를 UI/보고서 공통 모델로 반환. `RuleEngine`과 `AIEngine`은 같은 interface를 구현.
## 분석 대상
company/facility/region/industry/product. 분석 요청에 기준 시점, 적용 데이터 스냅샷, 엔진 종류·버전 기록. 공급 관계와 투자·제휴는 서로 다른 edge semantics; 단순 연결을 인과관계로 단정하지 않음.
## 3-Hop
BFS 탐색 시 사이클 방지, 노드·엣지 최대 개수 제한, 양방향 검색은 명시적 요청일 때만, 관계 유효기간·검증 상태 필터. 경로마다 edge evidence, 관계 유형, hop, known/possible/hypothesis를 반환.
## 초기 EWS(시연용 휴리스틱)
점수는 심각도·노출도·연결거리 등을 이용해 0–100 범위의 단순 가중 합으로 계산할 수 있으나 **검증된 예측확률이 아님**. 가중치·임계값은 config에 둬서 교체 가능하게 한다. `normal/watch/caution/alert` 4단계. 근거 부족 시 점수 null/판단 보류 가능. `confidence`와 위험도를 별도 저장; 미검증 증거만으로 공식 alert 확정 금지.
## 대체 공급처
HS4/HS6 + 산업·지역 매칭으로 후보 검색. 각 후보에 `match_reasons`, `unknown_capabilities`, `evidence_ids`, `verification_status` 포함. 후보 추천은 실제 공급 가능·납기·생산능력 보장이 아님.
## 표준 결과 모델
`analysis_id, target, as_of, engine, engine_version, risk:{score,level,confidence,is_heuristic}, paths[], impacts[], evidence_ids[], alternatives[], recommendations[], warnings[], generated_at, dataset_snapshot_id`. 원문 인용·출처는 별도 provenance 링크.
## 시각화·보고서
위험 요약 카드, 영향 경로 네트워크, 근거 패널, 대응 후보, 보고서 작성으로 이어지는 흐름. verified/reported/unverified/estimated/synthetic를 명시하고 확인된 영향/잠재적 노출/분석 가설을 구분.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

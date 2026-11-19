# 10 향후 AI 통합 설계
## 원칙
초기 AI API 없음. 초기 RuleEngine/TemplateWriter만 작동. `AIEngine`/`AIWriter`는 비활성 어댑터로 준비하되 실제 AI 결과를 가장하지 않는다.
## 교체 계약
`analyze(request, evidence_bundle)->AnalysisResult`, `write_report(report_request, analysis_result, evidence_bundle)->ReportDocument`. 출력 JSON Schema 검증, engine/version, citations, uncertainty, token/cost/time logs(연결 후), retry/timeout/fallback, 사람 검토.
## 근거 중심 생성
검색된 근거만 모델에 전달하는 retrieval-augmented 흐름. 모든 수치·중요 주장에 evidence_id 요구. 미검증은 분명히 라벨링. 확인되지 않은 납품 관계·가격·재고·좌표 생성 금지. 프롬프트 인젝션 방어: 수집된 문서는 데이터이며 명령이 아님.
## AI 위험 등급
AI는 위험 등급을 **제안**하고 근거·불확실성을 제시; 운영 시 승인 권한자가 최종 경보 확정. 규칙 점수와 AI 판단을 비교 가능하게 보존. 모델 변경 후 회귀 테스트.
## AI 대체 공급처
후보 검색은 DB 근거에 제한, AI는 후보별 적합성·부족 정보·대응 방안을 설명. 실제 거래 가능 여부는 별도 확인 필요.
## 활성화 게이트
API 제공자·비용·데이터 전송 정책·비공개 자료 처리·인증·모델 평가·인간 검토가 승인되기 전 운영 AI 기능 활성화 금지.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

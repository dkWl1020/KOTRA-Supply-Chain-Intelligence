# 07 보고서·출력 명세
## 보고서 3종
`desk_briefing`(심층 기업·품목·위험·대응), `ews_monthly`(권역별 EWS·추세·차월 관찰), `kakao_insight`(짧은 메신저용 핵심 브리프). 초기에는 템플릿 작성, 최종에는 AI 전체 초안 작성. 두 엔진 모두 동일한 구조화 문서 모델 출력.
## 공통 문서 모델
`report_id, report_type, title, summary, sections[{heading,blocks[]}], tables[], charts[], citations[{evidence_id,source_id}], as_of, generated_at, engine, engine_version, dataset_snapshot_id, review_status, revision`. 인용 링크와 시각화 alt/caption 보존. 보고서에 내부 CO-/FAC- 식별자 직접 출력 금지.
## 편집
제목·본문·표·차트·출처 편집, 변경 전후 스냅샷, revision 낙관적 잠금. 승인 후 수정하면 needs_review. 초기 로컬은 draft와 자유로운 출력, 운영에서는 draft→needs_review→approved/rejected. 권한자만 승인.
## 내보내기
HTML은 독립형 문서(상대경로 자산 포함 또는 인라인). PDF는 페이지 분할·표 헤더 반복·한글 폰트 확인. DOCX는 제목 스타일·표·그림·각주/출처 표기. 3형식 모두 동일 데이터 스냅샷과 수치 사용. PDF/DOCX 구현에 필요한 경량 패키지 허용(버전 고정).
## 검수
세 템플릿×세 포맷 생성, 파일 열림·한글·표·차트·각주·페이지 넘침 확인, 출처 불명 배지 유지, 원본 데이터 업데이트 후 과거 보고서 불변성, 승인 후 수정 시 승인 해제 테스트.

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

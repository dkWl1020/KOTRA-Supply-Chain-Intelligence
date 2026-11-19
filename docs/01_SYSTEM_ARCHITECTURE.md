# 01 시스템 아키텍처
## 컴포넌트
`run.py` CLI(init/validate/index/serve/import/collect); `api/server.py` 라우팅·정적 서빙; `api/store.py` SQLite 트랜잭션; `api/services/` 도메인별 서비스; `ingest/` 수집·파싱·정제·적재; `analysis/` rule/ai 어댑터; `reports/` 문서 모델·렌더러; `web/` ES 모듈 SPA; `tests/` 단위·통합·브라우저.
## 디렉터리
```text
KOTRA_final/
  run.py
  api/{server.py,store.py,routes/,services/}
  analysis/{interface.py,rule_engine.py,ai_engine.py}
  ingest/{sources/,collect.py,normalize.py,validate.py,load.py}
  db/{migrations/,seeds/}
  data/{raw/,staging/,curated/,manifests/}
  web/{index.html,styles/,js/{app.js,core/,components/,views/,visualizations/}}
  reports/{templates/,renderers/,models.py}
  runtime/  search_index/  tests/  docs/
```
## 프로세스 경계
로컬: 127.0.0.1에만 바인딩, SQLite WAL, 짧은 쓰기 트랜잭션, 단일 쓰기 큐 고려. API와 수집 작업은 명시적 트랜잭션으로 분리. 외부 접속은 인증·CSRF·CORS·요청 제한·TLS·백업을 도입하기 전 금지.
## 환경설정
`config.example.json`에 DB 경로, raw 디렉터리, 검색 제한, 포트, 엔진 모드, 최대 업로드 크기. 비밀키는 저장소에 커밋 금지.
## 의존성 정책
Python 표준 라이브러리 우선. PDF/DOCX, 브라우저 테스트, 지도 렌더링 등 필요한 의존성은 `requirements.txt`에 버전 고정·근거 기록. CDN 필수 의존성 금지(오프라인 시연 가능).

## 공통 구현 규칙
- Python 3.11+ / SQLite(FTS5) / HTML·CSS·Vanilla JavaScript. 초기 로컬 개발, 이후 배포.
- 원본 명세는 `../ORIGINAL_kotra.md`; 이 패키지는 1~7단계 합의 사항을 반영한 개정 설계. 원본과 충돌하면 `MASTER_SPEC.md`의 결정 로그 및 본 문서의 명시적 계약 우선.
- 수집되지 않은 자료를 확보했다고 주장하지 말 것. 예시·테스트·합성 데이터는 실제 데이터와 물리적/논리적으로 구분.
- 기능 미구현 시 가짜 성공 화면을 만들지 말고 명확한 비활성 상태·오류를 제공.
- 모든 신규 데이터의 출처/수집 시각/검증 상태를 추적. 검증 불가 데이터는 탐색 가능하되 확정 사실로 표시하지 않음.

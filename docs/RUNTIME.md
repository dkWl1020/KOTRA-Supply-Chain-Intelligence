# 실행과 구현 범위

이 폴더는 Python 표준 라이브러리와 SQLite로 실행하는 단일 담당자용 로컬 프로토타입이에요. 자료 CSV, 근거 조회, 사건 분석, 보고서 수정·검토·저장까지 한 흐름으로 연결했어요. `python run.py init`을 먼저 실행하고 `python run.py serve`로 `http://127.0.0.1:8000`을 열어요.

## 실행 순서

```bash
python run.py init
python run.py validate
python -m unittest discover -s tests -v
python run.py serve --port 8000
```

Python 3.11 이상과 SQLite FTS5가 필요해요. 별도 pip 패키지는 없어요. 다른 터미널에서 `python run.py collect-usgs`를 실행하면 공개 지진 피드를 수집해요. 예약 실행은 운영체제 작업 스케줄러에 이 명령을 등록하면 돼요. 재수집으로 기존 읽음·보류·검토 기록을 지우지 않아요.

## 자료와 저장

- CSV: 초기 입력 자료. 모든 파일을 한 트랜잭션으로 검사·적재하고, 오류가 생기면 전체 적재를 취소해요. 실패 내역은 `runtime/import_log.json`에 남아요.
- `runtime/kotra.sqlite`: 실제 운영 DB. 분석·검토·보고서·관심 대상·알림·수집 이력을 저장해요.
- `record_versions`와 `_record_snapshots`: 수정 시점과 당시 전체 기록을 보존해요. 분석에는 입력 자료·근거·원문의 당시 내용도 저장해요.
- `document_chunks.jsonl`과 `search_index/manifest.json`: 등록된 근거 발췌에서 재생성해요. 전체 원문 전문을 모두 검색한다고 주장하지 않아요. 텍스트 검색은 SQLite FTS5 저장과 Unicode 부분문자열 검색을 사용하며 임베딩 모델은 사용하지 않아요.
- 복합키 근거: `region_industries`의 record_id는 `US-WA|IND-AERO`처럼 스키마 기본키 순서로 연결하거나 JSON 배열 문자열을 사용해요.

## 분석과 보고서

기본 분석은 등록 근거를 모은 규칙 기반 미리보기예요. 생성형 AI를 사용하려면 `.env.example`을 `.env`로 복사하고 본인의 `OPENAI_API_KEY`, 사용할 `OPENAI_MODEL`을 설정한 뒤 화면에서 AI 실행을 선택해요. 키와 모델이 없으면 실행 오류로 표시하며 규칙 결과를 AI 결과로 바꾸지 않아요. 모델 호출에는 선택 기업과 연결된 자료·근거가 전달돼요.

AI 출력은 `schemas/analysis_result.json` 형식으로 받으며 근거 ID·대상 ID의 존재와 연결을 검증해요. ID 검증만으로 문장 의미 전체가 참임을 보장할 수 없으므로 담당자가 보고서를 검토해요. 기존 승인 이후 내용을 수정하면 버전이 올라가고 승인 상태가 해제돼요. 보고서는 HTML로 내보내고 브라우저 인쇄 기능으로 PDF를 만들 수 있어요. 자동 PDF 엔진은 포함하지 않았어요.

## 지도와 모니터링

시설 지도는 등록된 경도·위도 점을 표시해요. 좌표가 없는 시설은 점을 임의 생성하지 않아요. 정밀 도로 경로·사건 영향권을 계산하는 GIS 서비스는 구현 범위에 들어 있지 않아요. 지도 점의 근접성은 기업 피해를 의미하지 않아요.

USGS 수집기는 최근 7일 M2.5 이상 피드에서 서북부와 알래스카를 포함하는 좌표 범위의 사건을 수집해요. 이 범위는 행정경계 필터가 아니라 넓은 검색 범위예요. 수집된 사건은 관측으로 저장하며 기업 영향 연결을 자동으로 만들지 않아요. 수집 실패는 실패 기록으로 남기고 기존 사건을 삭제하거나 ‘사건 없음’으로 바꾸지 않아요.

알림은 관심 대상과 등록된 event_impacts가 연결되고 사건이 active/ongoing인 경우에만 생성돼요. 종료·만료·과거 시연 사건은 제외해요. 사건의 다른 제목을 같은 사건으로 자동 판별하는 범용 뉴스 중복 제거기는 제공하지 않으며 USGS의 고유 사건 ID를 사용해요.

## 운영 전 남은 결정

- 여러 직원의 로그인·권한·소속 분리는 미구현이에요. 현재 서버는 127.0.0.1에만 열고 단일 담당자 로컬 사용을 전제로 해요.
- 실서비스 배포는 인증, HTTPS, 영속 DB·원문 저장, 백업, 작업 큐를 붙인 후 진행해요. Python 기본 HTTP 서버는 실서비스 배포용이 아니에요.
- 실제 모델 호출은 사용자의 키·모델로 별도 실행해야 해요. 자동 테스트는 모델의 실 응답 품질·요금·장애를 검증하지 않아요.
- 담당자 미팅, 사용자 만족도 검증, 과제 발표는 코드로 대신 완료할 수 없는 팀 작업이에요.

## 구현에 참고한 문서

- [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create): HTTPS 요청과 JSON 응답 형식
- [OpenAI 구조화 출력](https://developers.openai.com/api/docs/guides/structured-outputs): JSON 모드와 별도 검증의 역할
- [USGS GeoJSON](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php): 사건 ID·발생 시각·규모·좌표 필드

# CURRENT STATE AUDIT — uploaded prototype snapshot

**Evidence:** `KOTRA_final(1).zip` uploaded in this conversation; not a live checkout of the GitHub repository. Reviewed on 2026-11-19. No assumption that GitHub HEAD matches this ZIP.

## Files and data
- CSV files in `data/`: **27**. Representative row counts: `companies` 38, `facilities` 35, `evidence` 473, `events` 10, `sources` 102, `statistics` 84, `relationships` 10. Counts are file rows, not independently verified real-world facts.
- Source-document markdown files: **102** (includes locally authored reference notes, not necessarily full original source text).
- SQL `001_initial.sql`: **35** `CREATE TABLE` declarations; `002_runtime_snapshots.sql` adds a runtime snapshot table. Actual schema is different from the v2 aspirational table names.
- Web assets: `web/app.js`, `web/index.html`, `web/style.css`.
- Existing docs: `ACCEPTANCE.md`, `BUILD_SEQUENCE.md`, `DATA_MODEL.md`, `DATA_POLICY.md`, `DECISIONS.md`, `GEOGRAPHY.md`, `RUNTIME.md` and JSON reports. Retained unchanged.

## Existing behavior from code
- `api/server.py`: loopback-only `ThreadingHTTPServer`; GET `/api/catalog`, `/api/data/{table}`, `/api/search`, `/api/map`, `/api/reports/{id}/export`; POST `/api/analyze`, `/api/reports`, `/api/watchlists`, `/api/refresh-alerts`, `/api/ingest/usgs`, `/api/reports/{id}/review`; PATCH `/api/reports/{id}`, `/api/alerts/{id}`.
- `query_data` currently materializes all rows in Python and filters/paginates afterward: scalability issue for hundreds of thousands of records.
- `query_data` explicitly includes Bay9 when North CA is selected for display; this conflicts with new nonoverlapping 22-county North CA definition. **Block geographic aggregations until fixed.**
- AI-related code exists according to README, but live external model behavior was not tested.
- GIS: README describes empty geography boundaries and only four verified facility points; verify live before any map-completeness claim.
- Automatic collector: USGS implemented; other sources are primarily configured/cataloged, not all automated.
- `.gitignore` in uploaded ZIP excluded `web/index.html`, `web/app.js`, `web/style.css` (!). Updated in this patch to allow frontend tracking. Check `git ls-files web` in actual repo.

## Tests executed in this workspace
- `python run.py validate`: `{"errors": [], "valid": true}`.
- `python -m unittest discover -s tests -v`: **10 tests, all passed** (1.461s in this environment).
- No visual browser QA, production security audit, high-volume load test, PDF/DOCX export verification, or live source refresh was performed.

## Not verified
- GitHub repository HEAD, commit history, previously tracked sensitive files, permissions, actual server deployment, and completeness/licensing of source datasets.

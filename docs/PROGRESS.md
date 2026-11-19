# PROGRESS — actual status

## Snapshot date: 2026-11-19
- Starting point: uploaded `KOTRA_final(1).zip`, not a verified live GitHub checkout.
- Existing Python/SQLite/Vanilla JS prototype, 27 data CSV files, SQL migrations, tests, and local UI **already exist**.
- Baseline `python run.py validate`: passed (`errors: []`, `valid: true`).
- Baseline `python -m unittest discover -s tests -v`: 10 tests passed.
- v2 specification docs merged into `docs/` without overwriting original docs.
- New: `AGENTS.md`, `CURRENT_STATE_AUDIT.md`, `GAP_ANALYSIS.md`, updated `TASKS.md`, updated `.gitignore`.
- **Not yet done:** GitHub commit/push, live browser QA, external data collection, code refactoring, actual schema migration, 22-county geography resolution.

## Next task
P00-04: compare this patch with GitHub working tree; check tracked files and sensitive material. Then P00-05 geography reconciliation before new regional aggregations.

## Verification commands
`python run.py validate`
`python -m unittest discover -s tests -v`
`git status`
`git ls-files web inputs runtime`

## Phase 01-01 — offline inventory tooling
- Added `scripts/audit_sources.py`, read-only catalog/CSV inventory and SHA-256 summary.
- Added `tests/test_source_audit.py` and `docs/PHASE_01_SOURCE_INVENTORY.md`.
- No new external datasets collected; licensing and endpoint availability not verified.
- P00-04/05/06 remain open; next P01-02 is idempotent ingestion manifest.

## Phase 01-02 — raw file importer
- Added `ingest/raw_import.py`, offline SHA-256 content-addressed raw file importer with SQLite provenance manifest.
- Added `tests/test_raw_import.py` and `docs/PHASE_01_RAW_INGEST.md`.
- Production DB, curated CSVs and existing APIs are unchanged.
- No external dataset collected and no AI integration added.
- Next: staging normalization and controlled curated promotion.

## Phase 01-03 — offline structured staging
- Added `ingest/staging.py` for CSV/JSON/JSONL schema validation, row-level errors, and idempotent staging batches.
- Added `tests/test_staging.py` and `docs/PHASE_01_STAGING.md`.
- No production DB changes and no new external data collection. Curated promotion remains deferred.

## Phase 01-04 — candidate promotion
- Added `ingest/curate.py`, candidate entity/observation tables in isolated `runtime/candidates.sqlite`, and regression tests.
- Production `runtime/kotra.sqlite` and curated CSVs are unchanged.
- Next: reviewed alias mapping and real dataset acquisition.

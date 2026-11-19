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

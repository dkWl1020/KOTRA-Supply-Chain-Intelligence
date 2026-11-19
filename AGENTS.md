# KOTRA development rules

1. Preserve existing functioning prototype and its baseline; never silently delete or overwrite source data.
2. Stack: Python 3.11+, SQLite/FTS5, vanilla HTML/CSS/JS; document any new dependency.
3. Read `docs/MASTER_SPEC.md`, `docs/CURRENT_STATE_AUDIT.md`, `docs/GAP_ANALYSIS.md`, `docs/TASKS.md`, and `docs/PROGRESS.md` before work.
4. Each task must state allowed files, acceptance tests, data provenance, and rollback plan. Avoid unrelated refactoring.
5. Never invent facilities, supply edges, coordinates, regulatory applicability, or source citations. Store uncertain claims as unverified, not as facts.
6. Keep historical incidents separate from active alerts; distinguish risk from confidence and synthetic records from real data.
7. Keep CA statewide, Bay9, and project-defined Northern CA aggregates distinct. Existing code currently conflates North CA/Bay9 for display: do not propagate into analytics.
8. Never expose a write-capable local-only server to the public internet. Add auth/RBAC and deployment hardening before external deployment.
9. Run `python run.py validate` and `python -m unittest discover -s tests -v` after relevant changes; report failures without claiming success.
10. Commit only reviewed files. `inputs/`, `.env`, `runtime/`, raw/staging data and generated outputs stay out of Git by default. If already committed, .gitignore does not remove their history.
11. Keep current implementation status and target specification separate. Update progress after each tested task.

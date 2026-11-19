# TASKS — prioritized implementation backlog (audited baseline)

## Phase 00 — baseline and reconciliation
- [x] P00-01 Audit uploaded ZIP, current API routes, SQL migrations, CSV inventory, and baseline tests.
- [x] P00-02 Add AGENTS.md and update .gitignore to stop excluding frontend assets.
- [x] P00-03 Preserve original prototype docs and merge v2 target docs without overwriting existing docs.
- [ ] P00-04 Check actual GitHub HEAD and `git ls-files`; inspect tracked `inputs/`, `.env`, `runtime/`, `web/` before committing.
- [ ] P00-05 Resolve Northern California 22-county vs existing 40-county assumption and Bay9 union; validate FIPS/GIS.
- [ ] P00-06 Produce current-to-target schema map and API request/response fixtures; decide compatibility migrations.

## Phase 01 — data first
- [ ] P01-01 Source inventory: license, update cadence, provenance, rate limits and permitted collection method.
- [ ] P01-02 Implement raw/staging/curated manifest and idempotent batch imports.
- [ ] P01-03 Expand actual datasets with domain-level QA and source citations.

## Phase 02 — backend/data scale
- [ ] P02-01 Additive SQLite migrations, indexes and evidence status.
- [ ] P02-02 Replace in-memory table filtering with SQL pagination and benchmarks.
- [ ] P02-03 API schema fixtures, search and admin import endpoints.

## Phase 03 — analysis/reports
- [ ] P03-01 3-hop graph and confidence-aware EWS, alternative candidates.
- [ ] P03-02 HTML/PDF/DOCX renderers and test fixtures.

## Phase 04 — UI and QA
- [ ] P04-01 Modern Hybrid design tokens and integrated home dashboard.
- [ ] P04-02 Map boundaries, clustering, draggable network, 7 existing screens.
- [ ] P04-03 Admin console and full browser E2E/visual/load QA.

## Deferred production
- [ ] P07-01 Optional AI adapters, AI report writing.
- [ ] P07-02 Auth/RBAC, scheduled collection and deployment security.

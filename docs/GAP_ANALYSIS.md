# GAP ANALYSIS — existing prototype vs v2 target

| Area | Existing prototype | v2 target | Priority / action |
|---|---|---|---|
| Database | Existing schema and 27 CSVs; `001_initial.sql` plus snapshot migration | Extensible raw/staging/curated, verification and import audit | P0: map current schema before additive migrations |
| Geography | North CA unresolved; server includes Bay9 in North display | Project-defined 22 North counties disjoint from Bay9, CA statewide benchmark | **P0: reconcile geography definitions and FIPS with authoritative source before implementation** |
| Search | `/api/search` plus generic row filtering | indexed unified search, constrained natural-language parsing, provenance | P1: contract and indexes; no claim of LLM search without model |
| API | Implemented local routes differ from v2 target route list | documented schemas, stable errors, pagination and admin APIs | P0: route inventory and compatibility mapping |
| Data scale | Generic endpoint loads full tables into memory | hundreds of thousands of records | P0: SQL-side filtering and keyset/offset pagination; benchmark |
| Frontend | Existing local UI, no verified modern hybrid home | 8 screens + admin, responsive, real map/graph | P1: preserve working views, add home and components incrementally |
| GIS | GeoJSON boundary acquisition incomplete | verified county geometry and marker clustering | P1: source licensed geometry and QA |
| Analysis | Existing analysis/report/watchlist/alerts | 3-hop graph, separated confidence, replaceable AI | P1: inventory existing algorithms, add versioned output schema |
| Reports | Existing HTML export, edit/review workflow | HTML/PDF/DOCX, eventual AI writing | P1: shared document model, actual format tests |
| Collection | USGS collector; catalog of other sources | large provenance-aware bulk datasets, later scheduled updates | P0: source catalog and raw manifests, batch collection |
| Roles | local single-operator mode | staff vs business roles, eventual approval | P2: no public deployment before auth/RBAC |
| Tests | 10 unittest cases pass | integration, E2E, visual, data integrity, load tests | P0: preserve baseline and add regression suite |

## Explicit reconciliation rules
- The v2 master document is a **target**, not a statement that all features exist. Existing README and tests describe the prototype.
- v2's proposed 22-county North CA definition conflicts with the prototype's unresolved 40-county assumption and Bay9 union behavior. This is a blocking specification decision to verify, not an already migrated database.
- Original KOTRA specification's 35-table count does not describe the current SQL schema; use migration inventory as current truth.
- Current source notes are not guaranteed to contain licensed full-text originals.
- Never count unverified claims as independently confirmed supply-chain edges.

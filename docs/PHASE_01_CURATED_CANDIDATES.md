# Phase 01-04: source-traceable candidate promotion

This step promotes accepted staging rows into `runtime/candidates.sqlite`, **not** the production `runtime/kotra.sqlite` database. It never asserts that candidate records represent verified suppliers or proven relationships.

## Usage

1. Import a CSV using `python -m ingest.raw_import FILE.csv --source-id SRC-EXAMPLE`.
2. Stage the SHA-256 returned by the importer using `python -m ingest.staging HASH --schema schema.json`.
3. Promote using `python -m ingest.curate BATCH_ID --entity-type company --name-field name`.

Entity types supported: `company`, `facility`, `product`, `industry`.

Each accepted staging row retains raw SHA-256, source ID, verification status, and normalized record. Identical normalized names within one entity type are grouped as candidate observations, not independently verified matches. Cross-language aliases and conflicting names **are not** auto-merged; a later human-reviewed alias reconciliation workflow is required.

Promotion is transactional and idempotent for each staging batch. Existing production CSV, production DB and report data remain untouched. The candidate store is runtime-only and should not be committed to Git.

## Limitations / next tasks

- No public web data collected in this phase.
- No canonical entity ID or production table write.
- No automated multilingual matching, address reconciliation or false-positive review UI.
- Add curated review and explicit mapping before promoting into the production DB.

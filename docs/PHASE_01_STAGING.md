# Phase 01-03 — offline staging validation

This is an **additive, offline** feature. It never writes to `runtime/kotra.sqlite`, curated CSVs, or production tables. It requires an object previously imported using `python -m ingest.raw_import`.

## Example

Create a JSON schema file, e.g. `schema.json`:

```json
{"columns":{"name":{"type":"text","required":true},"count":{"type":"integer"},"date":{"type":"date"}}}
```

Supported types: `text`, `integer`, `number` (stored as decimal string to avoid rounding), and `date` (`YYYY-MM-DD`). Fields not in the schema are not promoted; null/empty values are allowed unless `required` is true. Each invalid row is retained with errors and source row number. This is a basic schema, **not** full JSON Schema.

```powershell
python -m ingest.raw_import data/example.csv --source-id SRC-EXAMPLE
python -m ingest.staging <sha256-from-previous-command> --schema schema.json
```

The staging result is stored in `runtime/staging.sqlite` with per-row errors. Re-running the same raw hash and schema returns the existing batch. This phase does not perform entity resolution, provenance verification, or curated promotion. No public data has been newly collected.

## Limits and next work

- Default maximum 500,000 records per batch; parsing is currently buffered in memory and should be streamed in a later performance iteration.
- The raw object is SHA-256 checked before parsing. Corrupt objects fail closed.
- Unsupported file formats (`.md`, `.txt`) can be archived as raw evidence but not staged as structured records.
- `source_id` and verification metadata remain in the raw manifest; curated promotion must preserve provenance.
- Do not treat staged rows as verified facts or production data.

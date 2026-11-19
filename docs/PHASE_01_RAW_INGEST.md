# Phase 01-02 — offline raw-data ingestion

## Purpose
Import downloaded, **permitted** source files without touching the existing curated CSVs or `runtime/kotra.sqlite`. This is an ingestion foundation, not a web scraper and not a verified data source.

## Command

```powershell
python -m ingest.raw_import data/reference/example.csv --source-id SOURCE-ID --source-url https://example.org/data
```

A local file is required; the importer makes no network requests. Accepted extensions: CSV, JSON, JSONL, TXT and MD (up to 100 MiB per file by default). The original bytes are copied to `data/raw/objects/<sha256>.<ext>`. The manifest is kept at `runtime/raw_imports.sqlite`. Both locations are ignored by Git.

Each file's SHA-256 identifies its content. Reimporting the same bytes does not duplicate the object, but records a separate `import_attempts` entry with its own source metadata. Files start as `unverified` regardless of the claimed source. Raw imports are **not** automatically inserted into the production database, indexed for public search or used for EWS decisions.

## Limitations and next steps
- Not a full raw/staging/curated pipeline: staging normalization, domain validation, rollback of multi-file batches, and production promotion remain future work.
- A filesystem and SQLite DB are not a single atomic transaction. If the process stops between copying and manifest insertion, an orphan object may remain; a later maintenance command should reconcile it.
- The first import's filename/URL is preserved in `raw_imports`; every attempt is recorded separately.
- The source URL is metadata only and is not fetched or validated for licensing.
- Do not import private or restricted materials without authorization. Never commit `data/raw/` or `runtime/`.

## Verification

```powershell
python -m unittest discover -s tests -v
python run.py validate
```

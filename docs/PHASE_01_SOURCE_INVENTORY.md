# Phase 01-01 — Existing source and dataset inventory

## Scope
This task introduces an **offline, read-only** audit. It does **not** scrape external websites, download new records, or certify any licensing terms. The source catalog contains candidate collection channels; an endpoint listed there is not evidence that collection is currently operational.

## Run

```powershell
python scripts/audit_sources.py --output outputs/source_inventory.json
python -m unittest discover -s tests -v
python run.py validate
```

`outputs/` is ignored by Git. Review the JSON summary, including each CSV's row count and SHA-256. These counts include duplicates and do not establish unique verified entities. Source licensing, API availability, robots restrictions, credentials, and rate limits remain **manual review** until checked against official source documentation.

## Next tickets
- P01-02: raw/staging/curated import manifest with idempotent batch behavior.
- P01-03: source-specific collectors, each with permissions, provenance, and a controlled sample import before scaling.
- Resolve Phase 00 geography and Git tracking checks before producing regional aggregates or publishing source data.

#!/usr/bin/env python3
"""Offline, read-only audit of existing source catalog and reference CSV files."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('collection_source_id', 'publisher', 'access_method', 'endpoint_or_url', 'refresh_policy', 'enabled')


def read_csv(path):
    with path.open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f'Empty CSV: {path.name}')
        return reader.fieldnames, list(reader)


def audit(root=ROOT):
    catalog = root / 'data' / 'collection_sources.csv'
    fields, sources = read_csv(catalog)
    missing = sorted(set(REQUIRED) - set(fields))
    if missing:
        raise ValueError('Missing catalog columns: ' + ', '.join(missing))
    ids = [r['collection_source_id'].strip() for r in sources]
    duplicates = sorted(k for k, count in Counter(ids).items() if count > 1)
    if duplicates or any(not x for x in ids):
        raise ValueError(f'Invalid source IDs; duplicates={duplicates}')
    source_rows = []
    for r in sources:
        source_rows.append({
            'id': r['collection_source_id'],
            'publisher': r['publisher'],
            'method': r['access_method'],
            'url': r['endpoint_or_url'],
            'cadence': r['refresh_policy'],
            'enabled': r['enabled'] == '1',
            'credentials_env_name': r.get('credentials_env_name', ''),
            'collection_status': 'not_verified_in_this_audit',
            'license_status': 'needs_manual_review',
            'rate_limit_status': 'needs_manual_review',
        })
    datasets = []
    for path in sorted((root / 'data').glob('*.csv')):
        headers, rows = read_csv(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        datasets.append({'file': path.name, 'rows': len(rows), 'columns': len(headers), 'sha256': digest})
    return {'schema_version': 1, 'audit_type': 'offline_local_inventory',
            'sources': source_rows, 'datasets': datasets,
            'summary': {'source_count': len(sources), 'enabled_source_count': sum(x['enabled'] for x in source_rows),
                        'dataset_count': len(datasets), 'dataset_row_total': sum(x['rows'] for x in datasets)},
            'notes': ['CSV row counts are not verified unique real-world entities.',
                      'This audit does not download data or verify website terms, licensing or availability.',
                      'The source catalog lists candidate endpoints, not proven operational collectors.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, help='Optional JSON output file; otherwise stdout')
    args = parser.parse_args()
    result = audit(args.root)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
        print(f'Wrote {args.output}')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()

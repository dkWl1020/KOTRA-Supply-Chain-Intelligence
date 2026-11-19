"""Validate imported CSV/JSON/JSONL records into an isolated staging SQLite DB.

No writes to production kotra.sqlite or curated CSVs. Usage:
python -m ingest.staging <sha256> --root . --schema path/to/schema.json
"""
import argparse
import csv
import hashlib
import io
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _read_records(path):
    suffix = path.suffix.lower()
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        if suffix == '.csv':
            reader = csv.DictReader(f)
            if not reader.fieldnames or any(k is None or not k.strip() for k in reader.fieldnames):
                raise ValueError('CSV requires nonempty column headers')
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError('Duplicate CSV headers')
            for n, record in enumerate(reader, 2):
                yield n, record
        elif suffix == '.jsonl':
            for n, line in enumerate(f, 1):
                if line.strip():
                    item = json.loads(line)
                    if not isinstance(item, dict):
                        raise ValueError('JSONL entries must be objects')
                    yield n, item
        elif suffix == '.json':
            value = json.load(f)
            if not isinstance(value, list):
                raise ValueError('JSON root must be an array of objects')
            for n, item in enumerate(value, 1):
                if not isinstance(item, dict):
                    raise ValueError('JSON entries must be objects')
                yield n, item
        else:
            raise ValueError('Only CSV, JSON and JSONL can be staged')


def _normalize(value, kind):
    if value is None or value == '':
        return None
    if isinstance(value, str):
        value = value.strip()
    if kind == 'text':
        return str(value)
    if kind == 'integer':
        if isinstance(value, bool) or str(value).strip() != str(int(str(value).strip())):
            raise ValueError('invalid integer')
        return int(value)
    if kind == 'number':
        from decimal import Decimal, InvalidOperation
        try:
            v = Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError('invalid number') from exc
        if not v.is_finite():
            raise ValueError('nonfinite number')
        return str(v)
    if kind == 'date':
        return datetime.strptime(str(value), '%Y-%m-%d').date().isoformat()
    raise ValueError('Unsupported schema type: ' + kind)


def _schema(schema_path):
    schema = json.loads(Path(schema_path).read_text(encoding='utf-8'))
    if not isinstance(schema, dict) or not isinstance(schema.get('columns'), dict) or not schema['columns']:
        raise ValueError('Schema requires columns mapping')
    allowed = {'text', 'integer', 'number', 'date'}
    for name, cfg in schema['columns'].items():
        if not isinstance(name, str) or not isinstance(cfg, dict) or cfg.get('type') not in allowed:
            raise ValueError('Invalid schema column')
    return schema


def stage_import(digest, *, root, schema_path, max_rows=500000):
    root = Path(root).resolve()
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid SHA-256')
    if max_rows < 1:
        raise ValueError('max_rows must be positive')
    schema = _schema(schema_path)
    schema_hash = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
    raw_db = root / 'runtime' / 'raw_imports.sqlite'
    if not raw_db.is_file():
        raise FileNotFoundError('Raw import manifest missing')
    with closing(sqlite3.connect(raw_db)) as db:
        row = db.execute('SELECT stored_path FROM raw_imports WHERE sha256=?', (digest,)).fetchone()
    if row is None:
        raise ValueError('Unknown raw import hash')
    raw_root = (root / 'data' / 'raw' / 'objects').resolve()
    path = (root / row[0]).resolve()
    if not path.is_relative_to(raw_root) or not path.is_file() or path.is_symlink():
        raise ValueError('Unsafe or missing raw object')
    if _hash(path) != digest:
        raise ValueError('Raw object integrity mismatch')
    staging_db = root / 'runtime' / 'staging.sqlite'
    staging_db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(staging_db)) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('''CREATE TABLE IF NOT EXISTS staging_batches (
            batch_id INTEGER PRIMARY KEY, raw_sha256 TEXT NOT NULL,
            schema_sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
            accepted INTEGER NOT NULL, rejected INTEGER NOT NULL,
            UNIQUE(raw_sha256, schema_sha256))''')
        db.execute('''CREATE TABLE IF NOT EXISTS staging_rows (
            batch_id INTEGER NOT NULL REFERENCES staging_batches(batch_id),
            source_row INTEGER NOT NULL, normalized_json TEXT, errors_json TEXT,
            PRIMARY KEY(batch_id, source_row))''')
        prior = db.execute('SELECT batch_id, accepted, rejected FROM staging_batches WHERE raw_sha256=? AND schema_sha256=?',
                           (digest, schema_hash)).fetchone()
        if prior:
            return {'status': 'existing', 'batch_id': prior[0], 'accepted': prior[1], 'rejected': prior[2]}
        records = []
        accepted = rejected = 0
        for idx, (line, record) in enumerate(_read_records(path), 1):
            if idx > max_rows:
                raise ValueError('Record count exceeds max_rows; nothing staged')
            result, errors = {}, []
            for col, cfg in schema['columns'].items():
                try:
                    value = _normalize(record.get(col), cfg['type'])
                    if cfg.get('required') and value is None:
                        raise ValueError('required value missing')
                    result[col] = value
                except (ValueError, TypeError, OverflowError) as exc:
                    errors.append(f'{col}: {exc}')
            if None in record:
                errors.append('unexpected extra CSV values')
            if errors:
                rejected += 1
            else:
                accepted += 1
            records.append((line, json.dumps(result, ensure_ascii=False) if not errors else None,
                            json.dumps(errors, ensure_ascii=False) if errors else None))
        with db:
            cursor = db.execute('INSERT INTO staging_batches(raw_sha256,schema_sha256,created_at,accepted,rejected) VALUES (?,?,?,?,?)',
                                (digest, schema_hash, _utc(), accepted, rejected))
            batch_id = cursor.lastrowid
            db.executemany('INSERT INTO staging_rows(batch_id,source_row,normalized_json,errors_json) VALUES (?,?,?,?)',
                           ((batch_id, *r) for r in records))
        return {'status': 'staged', 'batch_id': batch_id, 'accepted': accepted, 'rejected': rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sha256')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--schema', type=Path, required=True)
    parser.add_argument('--max-rows', type=int, default=500000)
    args = parser.parse_args()
    print(json.dumps(stage_import(args.sha256, root=args.root, schema_path=args.schema,
                                  max_rows=args.max_rows), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

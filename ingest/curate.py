"""Promote accepted staging rows to an isolated, source-traceable candidate catalog.

This is NOT the production companies/facilities DB. Candidate matches require review
before any canonical supply-chain relationship is asserted.
"""
import argparse
import json
import re
import sqlite3
import unicodedata
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"company", "facility", "product", "industry"}


def normalized_name(value):
    if not isinstance(value, str):
        raise ValueError("name must be a string")
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    value = re.sub(r"\s+", " ", value)
    if not value:
        raise ValueError("name cannot be empty")
    return value


def _create(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS candidate_entities (
        candidate_id INTEGER PRIMARY KEY,
        entity_type TEXT NOT NULL,
        canonical_name TEXT NOT NULL,
        normalized_name TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'unverified',
        created_at TEXT NOT NULL,
        UNIQUE(entity_type, normalized_name)
    );
    CREATE TABLE IF NOT EXISTS candidate_aliases (
        entity_type TEXT NOT NULL,
        normalized_alias TEXT NOT NULL,
        candidate_id INTEGER NOT NULL REFERENCES candidate_entities(candidate_id),
        original_alias TEXT NOT NULL,
        PRIMARY KEY(entity_type, normalized_alias)
    );
    CREATE TABLE IF NOT EXISTS candidate_observations (
        batch_id INTEGER NOT NULL,
        source_row INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL REFERENCES candidate_entities(candidate_id),
        raw_sha256 TEXT NOT NULL,
        source_id TEXT,
        verification_status TEXT NOT NULL,
        record_json TEXT NOT NULL,
        PRIMARY KEY(batch_id, source_row)
    );
    CREATE TABLE IF NOT EXISTS promotion_batches (
        batch_id INTEGER PRIMARY KEY,
        entity_type TEXT NOT NULL,
        promoted_count INTEGER NOT NULL,
        skipped_count INTEGER NOT NULL,
        promoted_at TEXT NOT NULL
    );
    """)


def promote_batch(batch_id, *, root, entity_type, name_field='name'):
    if entity_type not in ALLOWED:
        raise ValueError('Unsupported entity_type')
    if not isinstance(batch_id, int) or isinstance(batch_id, bool) or batch_id < 1:
        raise ValueError('Invalid batch_id')
    if not isinstance(name_field, str) or not name_field.isidentifier():
        raise ValueError('Invalid name_field')
    root = Path(root).resolve()
    staging_path = root / 'runtime' / 'staging.sqlite'
    raw_path = root / 'runtime' / 'raw_imports.sqlite'
    if not staging_path.is_file() or not raw_path.is_file():
        raise FileNotFoundError('Staging or raw manifest missing')
    with closing(sqlite3.connect(staging_path)) as staging, closing(sqlite3.connect(raw_path)) as raw:
        batch = staging.execute('SELECT raw_sha256, accepted FROM staging_batches WHERE batch_id=?', (batch_id,)).fetchone()
        if batch is None:
            raise ValueError('Unknown staging batch')
        manifest = raw.execute('SELECT first_source_id, verification_status, stored_path FROM raw_imports WHERE sha256=?', (batch[0],)).fetchone()
        if manifest is None:
            raise ValueError('Missing raw provenance')
        from ingest.staging import _hash
        raw_object = (root / manifest[2]).resolve()
        raw_dir = (root / 'data' / 'raw' / 'objects').resolve()
        if not raw_object.is_relative_to(raw_dir) or not raw_object.is_file() or raw_object.is_symlink() or _hash(raw_object) != batch[0]:
            raise ValueError('Raw provenance integrity mismatch')
        rows = staging.execute('SELECT source_row, normalized_json FROM staging_rows WHERE batch_id=? AND errors_json IS NULL ORDER BY source_row', (batch_id,)).fetchall()
        if len(rows) != batch[1]:
            raise ValueError('Staging accepted-count mismatch')
        prepared = []
        for line, payload in rows:
            record = json.loads(payload)
            name = record.get(name_field)
            prepared.append((line, name, normalized_name(name), payload))
    dest = root / 'runtime' / 'candidates.sqlite'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(dest, timeout=30)) as db:
        db.execute('PRAGMA foreign_keys=ON')
        _create(db)
        prior = db.execute('SELECT entity_type, promoted_count, skipped_count FROM promotion_batches WHERE batch_id=?', (batch_id,)).fetchone()
        if prior:
            if prior[0] != entity_type:
                raise ValueError('Batch already promoted with different entity_type')
            return {'status': 'existing', 'batch_id': batch_id, 'promoted': prior[1], 'skipped': prior[2]}
        now = datetime.now(timezone.utc).isoformat()
        with db:
            for line, name, key, payload in prepared:
                found = db.execute('SELECT candidate_id FROM candidate_aliases WHERE entity_type=? AND normalized_alias=?', (entity_type, key)).fetchone()
                if found:
                    candidate_id = found[0]
                else:
                    cursor = db.execute('INSERT INTO candidate_entities(entity_type,canonical_name,normalized_name,created_at) VALUES (?,?,?,?)', (entity_type, name, key, now))
                    candidate_id = cursor.lastrowid
                    db.execute('INSERT INTO candidate_aliases VALUES (?,?,?,?)', (entity_type, key, candidate_id, name))
                db.execute('INSERT INTO candidate_observations VALUES (?,?,?,?,?,?,?)', (batch_id, line, candidate_id, batch[0], manifest[0], manifest[1], payload))
            db.execute('INSERT INTO promotion_batches VALUES (?,?,?,?,?)', (batch_id, entity_type, len(prepared), 0, now))
        return {'status': 'promoted', 'batch_id': batch_id, 'promoted': len(prepared), 'skipped': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('batch_id', type=int)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--entity-type', choices=sorted(ALLOWED), required=True)
    p.add_argument('--name-field', default='name')
    args = p.parse_args()
    print(json.dumps(promote_batch(args.batch_id, root=args.root, entity_type=args.entity_type, name_field=args.name_field), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

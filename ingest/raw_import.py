"""Offline raw file ingestion; does not modify production SQLite or curated CSVs.

Usage: python -m ingest.raw_import path/to/file.csv --source-id SRC-EXAMPLE
"""
import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED = {'.csv', '.json', '.jsonl', '.txt', '.md'}
DEFAULT_LIMIT = 100 * 1024 * 1024


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _connect(db_path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute('PRAGMA busy_timeout=30000')
    conn.execute("""CREATE TABLE IF NOT EXISTS raw_imports (
        sha256 TEXT PRIMARY KEY,
        original_filename TEXT NOT NULL,
        stored_path TEXT NOT NULL,
        byte_size INTEGER NOT NULL,
        first_source_id TEXT,
        first_source_url TEXT,
        verification_status TEXT NOT NULL DEFAULT 'unverified',
        imported_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS import_attempts (
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sha256 TEXT NOT NULL REFERENCES raw_imports(sha256),
        original_filename TEXT NOT NULL,
        source_id TEXT,
        source_url TEXT,
        collected_at TEXT,
        imported_at TEXT NOT NULL,
        result TEXT NOT NULL CHECK(result IN ('inserted','duplicate'))
    )""")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_attempts_sha ON import_attempts(sha256)')
    conn.commit()
    return conn


def ingest_file(source_path, *, root, source_id=None, source_url=None, collected_at=None,
                max_bytes=DEFAULT_LIMIT):
    source_path = Path(source_path).resolve(strict=True)
    root = Path(root).resolve()
    if not source_path.is_file() or source_path.is_symlink():
        raise ValueError('Input must be a regular non-symlink file')
    if source_path.suffix.lower() not in SUPPORTED:
        raise ValueError('Unsupported file extension')
    size = source_path.stat().st_size
    if size > max_bytes:
        raise ValueError('Input exceeds configured byte limit')
    if source_url and not source_url.startswith(('https://', 'http://')):
        raise ValueError('Source URL must start with http:// or https://')
    digest = _sha256(source_path)
    raw_dir = root / 'data' / 'raw' / 'objects'
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / (digest + source_path.suffix.lower())
    db_path = root / 'runtime' / 'raw_imports.sqlite'
    conn = _connect(db_path)
    try:
        existing = conn.execute('SELECT stored_path FROM raw_imports WHERE sha256=?', (digest,)).fetchone()
        if existing:
            if not (root / existing[0]).is_file():
                raise RuntimeError('Manifest references missing raw object; manual repair required')
            if _sha256(root / existing[0]) != digest:
                raise RuntimeError('Stored raw object hash mismatch; manual repair required')
            outcome = 'duplicate'
        else:
            # Write into the destination directory then atomically publish.
            fd, temporary = tempfile.mkstemp(prefix='.incoming-', dir=raw_dir)
            try:
                with os.fdopen(fd, 'wb') as out, source_path.open('rb') as inp:
                    shutil.copyfileobj(inp, out, length=1024 * 1024)
                if _sha256(Path(temporary)) != digest:
                    raise RuntimeError('Input changed during copy')
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            relative = target.relative_to(root).as_posix()
            with conn:
                conn.execute("""INSERT INTO raw_imports
                    (sha256,original_filename,stored_path,byte_size,first_source_id,first_source_url,imported_at)
                    VALUES (?,?,?,?,?,?,?)""",
                    (digest, source_path.name, relative, size, source_id, source_url, _now()))
            outcome = 'inserted'
        with conn:
            conn.execute("""INSERT INTO import_attempts
                (sha256,original_filename,source_id,source_url,collected_at,imported_at,result)
                VALUES (?,?,?,?,?,?,?)""",
                (digest, source_path.name, source_id, source_url, collected_at, _now(), outcome))
        return {'status': outcome, 'sha256': digest, 'bytes': size,
                'stored_path': existing[0] if existing else relative,
                'verification_status': 'unverified'}
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-id')
    parser.add_argument('--source-url')
    parser.add_argument('--collected-at', help='Original source timestamp (ISO 8601)')
    parser.add_argument('--max-bytes', type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()
    print(json.dumps(ingest_file(args.file, root=args.root, source_id=args.source_id,
        source_url=args.source_url, collected_at=args.collected_at, max_bytes=args.max_bytes),
        ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

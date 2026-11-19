"""Staging import integration tests, including Windows-safe SQLite cleanup."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from ingest.raw_import import ingest_file
from ingest.staging import stage_import


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.schema = self.root / 'schema.json'
        self.schema.write_text(json.dumps({'columns': {
            'name': {'type': 'text', 'required': True},
            'count': {'type': 'integer', 'required': True},
            'date': {'type': 'date'}}}), encoding='utf-8')

    def _import(self, name, content):
        p = self.root / name
        p.write_text(content, encoding='utf-8')
        return ingest_file(p, root=self.root)['sha256']

    def test_accept_reject_and_idempotency(self):
        digest = self._import('records.csv', 'name,count,date\nAlpha,0,2026-01-01\nBeta,wrong,2026-01-02\n')
        first = stage_import(digest, root=self.root, schema_path=self.schema)
        self.assertEqual((first['accepted'], first['rejected']), (1, 1))
        again = stage_import(digest, root=self.root, schema_path=self.schema)
        self.assertEqual(again['status'], 'existing')
        with closing(sqlite3.connect(self.root / 'runtime' / 'staging.sqlite')) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM staging_rows').fetchone()[0], 2)
            row = db.execute('SELECT normalized_json FROM staging_rows WHERE errors_json IS NULL').fetchone()[0]
            self.assertEqual(json.loads(row)['count'], 0)

    def test_jsonl_and_json(self):
        for name, body in [('records.jsonl', '{"name":"A","count":2}\n'),
                           ('records.json', '[{"name":"B","count":3}]')]:
            digest = self._import(name, body)
            self.assertEqual(stage_import(digest, root=self.root, schema_path=self.schema)['accepted'], 1)

    def test_limit_rolls_back(self):
        digest = self._import('many.csv', 'name,count\nA,1\nB,2\n')
        with self.assertRaises(ValueError):
            stage_import(digest, root=self.root, schema_path=self.schema, max_rows=1)
        with closing(sqlite3.connect(self.root / 'runtime' / 'staging.sqlite')) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM staging_batches').fetchone()[0], 0)

    def test_reject_corrupt_raw(self):
        digest = self._import('data.csv', 'name,count\nA,1\n')
        p = next((self.root / 'data' / 'raw' / 'objects').iterdir())
        p.write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            stage_import(digest, root=self.root, schema_path=self.schema)

    def test_schema_required(self):
        digest = self._import('data.csv', 'name,count\nA,1\n')
        self.schema.write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError):
            stage_import(digest, root=self.root, schema_path=self.schema)


if __name__ == '__main__':
    unittest.main()

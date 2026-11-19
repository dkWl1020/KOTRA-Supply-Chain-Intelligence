"""Raw ingestion safety, provenance and idempotency tests."""
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from ingest.raw_import import ingest_file


class RawImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'incoming.csv'
        self.source.write_text('name,value\nA,1\n', encoding='utf-8')

    def test_import_and_duplicate_preserve_attempts(self):
        first = ingest_file(self.source, root=self.root, source_id='S1')
        second = ingest_file(self.source, root=self.root, source_id='S2')
        self.assertEqual(first['status'], 'inserted')
        self.assertEqual(second['status'], 'duplicate')
        self.assertEqual(first['sha256'], second['sha256'])
        with closing(sqlite3.connect(self.root / 'runtime' / 'raw_imports.sqlite')) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM raw_imports').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT count(*) FROM import_attempts').fetchone()[0], 2)

    def test_different_content_creates_distinct_object(self):
        a = ingest_file(self.source, root=self.root)
        self.source.write_text('name,value\nB,2\n', encoding='utf-8')
        b = ingest_file(self.source, root=self.root)
        self.assertNotEqual(a['sha256'], b['sha256'])

    def test_disallowed_extension_and_oversize(self):
        self.source.rename(self.root / 'incoming.exe')
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            ingest_file(self.root / 'incoming.exe', root=self.root)
        self.source.write_bytes(b'1234')
        with self.assertRaisesRegex(ValueError, 'limit'):
            ingest_file(self.source, root=self.root, max_bytes=2)

    def test_corrupt_stored_object_fails_closed(self):
        result = ingest_file(self.source, root=self.root)
        (self.root / result['stored_path']).write_text('tampered', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'hash mismatch'):
            ingest_file(self.source, root=self.root)

    def test_invalid_source_url(self):
        with self.assertRaisesRegex(ValueError, 'Source URL'):
            ingest_file(self.source, root=self.root, source_url='file:///private')


if __name__ == '__main__':
    unittest.main()

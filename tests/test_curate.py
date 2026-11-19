import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from ingest.raw_import import ingest_file
from ingest.staging import stage_import
from ingest.curate import promote_batch, normalized_name


class CurateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.schema = self.root / 'schema.json'
        self.schema.write_text(json.dumps({'columns': {'name': {'type': 'text', 'required': True}, 'region': {'type': 'text'}}}))

    def batch(self, filename, contents):
        path = self.root / filename
        path.write_text(contents, encoding='utf-8')
        digest = ingest_file(path, root=self.root, source_id='SRC-TEST')['sha256']
        return stage_import(digest, root=self.root, schema_path=self.schema)['batch_id']

    def test_provenance_and_idempotency(self):
        batch = self.batch('a.csv', 'name,region\nAlpha,WA\nALPHA,OR\nBeta,ID\n')
        result = promote_batch(batch, root=self.root, entity_type='company')
        self.assertEqual(result['promoted'], 3)
        self.assertEqual(promote_batch(batch, root=self.root, entity_type='company')['status'], 'existing')
        with closing(sqlite3.connect(self.root / 'runtime' / 'candidates.sqlite')) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM candidate_entities').fetchone()[0], 2)
            self.assertEqual(db.execute('SELECT count(*) FROM candidate_observations').fetchone()[0], 3)
            self.assertEqual(db.execute('SELECT DISTINCT verification_status FROM candidate_observations').fetchone()[0], 'unverified')

    def test_rejected_rows_excluded(self):
        batch = self.batch('a.csv', 'name,region\nAlpha,WA\n,OR\n')
        self.assertEqual(promote_batch(batch, root=self.root, entity_type='facility')['promoted'], 1)

    def test_missing_name_rolls_back(self):
        batch = self.batch('a.csv', 'name,region\nAlpha,WA\n,OR\n')
        with self.assertRaises(ValueError):
            promote_batch(batch, root=self.root, entity_type='company', name_field='missing')
        self.assertFalse((self.root / 'runtime' / 'candidates.sqlite').exists())

    def test_invalid_entity_and_batch(self):
        with self.assertRaises(ValueError):
            promote_batch(1, root=self.root, entity_type='event')
        with self.assertRaises(ValueError):
            promote_batch(0, root=self.root, entity_type='company')

    def test_normalization(self):
        self.assertEqual(normalized_name('  ＡＬＰＨＡ  '), 'alpha')
        self.assertNotEqual(normalized_name('SK hynix'), normalized_name('하이닉스'))


if __name__ == '__main__':
    unittest.main()

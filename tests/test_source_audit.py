"""Offline tests for Phase 01 source inventory."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.audit_sources import audit


class SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()

    def write(self, name, header, rows):
        with (self.root / 'data' / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    def test_inventory_counts_and_disables(self):
        self.write('collection_sources.csv',
                   ['collection_source_id', 'publisher', 'access_method', 'endpoint_or_url', 'refresh_policy', 'enabled'],
                   [['S1', 'Agency', 'api', 'https://example.org', 'daily', '0']])
        self.write('companies.csv', ['id', 'name'], [['1', 'A'], ['2', 'B']])
        result = audit(self.root)
        self.assertEqual(result['summary']['source_count'], 1)
        self.assertEqual(result['summary']['enabled_source_count'], 0)
        self.assertEqual(result['summary']['dataset_row_total'], 3)
        self.assertEqual(result['sources'][0]['license_status'], 'needs_manual_review')

    def test_duplicate_source_id_rejected(self):
        self.write('collection_sources.csv',
                   ['collection_source_id', 'publisher', 'access_method', 'endpoint_or_url', 'refresh_policy', 'enabled'],
                   [['S1', 'A', 'api', 'https://a.org', 'daily', '0'], ['S1', 'B', 'api', 'https://b.org', 'daily', '0']])
        with self.assertRaisesRegex(ValueError, 'duplicates'):
            audit(self.root)

    def test_missing_required_column_rejected(self):
        self.write('collection_sources.csv', ['collection_source_id'], [['S1']])
        with self.assertRaisesRegex(ValueError, 'Missing catalog columns'):
            audit(self.root)


if __name__ == '__main__':
    unittest.main()

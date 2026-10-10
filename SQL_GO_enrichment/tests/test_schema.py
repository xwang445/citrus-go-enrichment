"""Portable schema/query smoke tests; no private inputs or R installation required."""
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript((ROOT / 'sql/schema.sql').read_text())
        self.db.executescript((ROOT / 'sql/indexes.sql').read_text())
        self.db.execute('INSERT INTO sources VALUES(1,?,?,?,?)', ('synthetic_fixture', 'fixture', 'test', 3))
        self.db.executemany('INSERT INTO genes VALUES(?,?,?,?,?,?)', [
            ('synthetic_A', 'scaffold_test', 10, 20, '+', 1),
            ('synthetic_B', 'scaffold_test', 30, 40, '-', 1),
            ('synthetic_C', 'scaffold_test', 50, 60, '+', 1)])
        self.db.executemany('INSERT INTO traits VALUES(?,?,NULL)', [(1, 'trait_A'), (2, 'trait_B')])
        self.db.executemany('INSERT INTO trait_genes VALUES(?,?)', [(1, 'synthetic_A'), (1, 'synthetic_B'), (2, 'synthetic_A'), (2, 'synthetic_C')])
        self.db.execute("INSERT INTO go_terms(go_id,go_name,ontology) VALUES('GO:0000001','synthetic term','BP')")
        self.db.execute("INSERT INTO gene_go VALUES('synthetic_A','GO:0000001',1)")

    def tearDown(self):
        self.db.close()

    def query(self, number):
        sql = next((ROOT / 'sql/queries').glob(f'{number:02d}_*.sql')).read_text()
        return self.db.execute(sql, dict(trait='trait_A', chromosome='scaffold_test', start=20, end=30)).fetchall()

    def test_all_queries_execute(self):
        for number in range(1, 11):
            with self.subTest(number=number):
                self.assertIsInstance(self.query(number), list)

    def test_join_coverage_shared_and_missing(self):
        self.assertEqual(len(self.query(2)), 1)
        self.assertEqual(self.query(3), [('synthetic_A', 2)])
        self.assertEqual(self.query(6), [('trait_A', 2, 1, .5), ('trait_B', 2, 1, .5)])
        self.assertEqual(self.query(7), [('trait_A', 'synthetic_B'), ('trait_B', 'synthetic_C')])

    def test_interval_includes_both_boundaries(self):
        self.assertEqual({row[0] for row in self.query(9)}, {'synthetic_A', 'synthetic_B'})

    def test_constraints(self):
        self.assertEqual(self.db.execute('PRAGMA foreign_keys').fetchone(), (1,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO trait_genes VALUES(1,'synthetic_A')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO trait_genes VALUES(1,'missing')")
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])

if __name__ == '__main__':
    unittest.main(verbosity=2)

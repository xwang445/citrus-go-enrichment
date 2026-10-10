import sys,unittest,tempfile,subprocess,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from common import connect,read,ANNOT,SOURCE,norm

class PipelineTests(unittest.TestCase):
 def setUp(self):self.c=connect()
 def tearDown(self):self.c.close()
 def test_snapshot_counts(self):
  for t,n in {'genes':24533,'traits':16,'trait_genes':3120,'gene_go':38855,'go_terms':2441,'associations':280,'association_genes':3499,'annotation_records':34980}.items():
   self.assertEqual(self.c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0],n)
 def test_foreign_keys(self):
  self.assertEqual(self.c.execute('PRAGMA foreign_keys').fetchone()[0],1)
  self.assertEqual(self.c.execute('PRAGMA foreign_key_check').fetchall(),[])
  with self.assertRaises(sqlite3.IntegrityError):self.c.execute('INSERT INTO trait_genes VALUES(999999,?)',('not_a_gene',))
 def test_primary_keys(self):
  g=self.c.execute('SELECT gene_id FROM genes LIMIT 1').fetchone()[0]
  with self.assertRaises(sqlite3.IntegrityError):self.c.execute('INSERT INTO genes(gene_id) VALUES(?)',(g,))
 def test_coordinate_constraints(self):
  with self.assertRaises(sqlite3.IntegrityError):self.c.execute('INSERT INTO genes(gene_id,start_position,end_position) VALUES(?,?,?)',('invalid',100,1))
 def test_join_and_missing(self):
  pairs=set(map(tuple,read(ANNOT/'Cclementina_CPBD_gene2GO.tsv')[['gene_id','GO_ID']].values));bg={g for g,go in pairs}
  for p in SOURCE.glob('*_candidate_genes.txt'):
   trait=p.name.removesuffix('_candidate_genes.txt');genes=set(map(norm,p.read_text().split()))
   actual=set(self.c.execute('SELECT gg.gene_id,gg.go_id FROM trait_genes tg JOIN traits t USING(trait_id) JOIN gene_go gg USING(gene_id) WHERE t.trait_name=?',(trait,)))
   self.assertEqual(actual,{(g,go) for g,go in pairs if g in genes})
   missing={r[0] for r in self.c.execute('SELECT tg.gene_id FROM trait_genes tg JOIN traits t USING(trait_id) LEFT JOIN gene_go gg USING(gene_id) WHERE t.trait_name=? AND gg.go_id IS NULL',(trait,))}
   self.assertEqual(missing,genes-bg)
 def test_repeatable_build(self):
  with tempfile.TemporaryDirectory() as tmp:
   tables=[r[0] for r in self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT IN ('analysis_runs','enrichment_results','enrichment_genes')")]
   for name in ['first','second']:
    db=Path(tmp)/(name+'.sqlite');cmd=[sys.executable,str(ROOT/'scripts/01_build_database.py'),'--database',str(db)]
    subprocess.run(cmd,check=True,capture_output=True)
    before=db.read_bytes();subprocess.run(cmd,check=True,capture_output=True);self.assertEqual(before,db.read_bytes())
    with connect(db) as other:
     for t in tables:self.assertEqual(self.c.execute(f'SELECT * FROM {t} ORDER BY rowid').fetchall(),other.execute(f'SELECT * FROM {t} ORDER BY rowid').fetchall(),t)
 def test_no_import_issues(self):self.assertEqual(len(read_csv_issues()),0)

def read_csv_issues():
 import pandas as pd
 return pd.read_csv(ROOT/'results/import_issues.csv')
if __name__=='__main__':unittest.main(verbosity=2)

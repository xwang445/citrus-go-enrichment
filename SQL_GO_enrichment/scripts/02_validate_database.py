from common import *
import argparse

def validate(c):
 checks=[]
 def check(name,ok,detail):checks.append(dict(check=name,passed=bool(ok),detail=str(detail)))
 check('foreign_key_enforcement',c.execute('PRAGMA foreign_keys').fetchone()[0]==1,'per-connection enforcement')
 fk=c.execute('PRAGMA foreign_key_check').fetchall();check('foreign_keys',not fk,fk)
 integrity=c.execute('PRAGMA integrity_check').fetchone()[0];check('integrity',integrity=='ok',integrity)
 for table,cols in [('genes','gene_id'),('traits','trait_id'),('go_terms','go_id'),('gene_go','gene_id,go_id'),('trait_genes','trait_id,gene_id')]:
  dup=c.execute(f'SELECT COUNT(*) FROM (SELECT {cols} FROM {table} GROUP BY {cols} HAVING COUNT(*)>1)').fetchone()[0];check(table+'_uniqueness',dup==0,dup)
 mapping=read(ANNOT/'Cclementina_CPBD_gene2GO.tsv');pairs=set(map(tuple,mapping[['gene_id','GO_ID']].values));actual=set(c.execute('SELECT gene_id,go_id FROM gene_go'));check('mapping_pairs',pairs==actual,f'{len(actual)} pairs')
 names=read(ANNOT/'Cclementina_GO_terms.tsv');expected=set(map(tuple,names[['GO_ID','Current_GO_ID','Description','Ontology','Source']].values));check('term_metadata',expected==set(c.execute('SELECT go_id,current_go_id,go_name,ontology,annotation_provider FROM go_terms')),len(expected))
 bg=set(mapping.gene_id);check('background',bg=={r[0] for r in c.execute('SELECT gene_id FROM background_genes')},len(bg))
 allgenes=set();total=0
 for p in sorted(SOURCE.glob('*_candidate_genes.txt')):
  name=p.name.removesuffix('_candidate_genes.txt');expected=set(map(norm,p.read_text().split()));allgenes|=expected;total+=len(expected)
  actual={r[0] for r in c.execute('SELECT gene_id FROM trait_genes JOIN traits USING(trait_id) WHERE trait_name=?',(name,))};check(name+'_candidates',actual==expected,len(actual))
  joined=set(c.execute('SELECT gg.gene_id,gg.go_id FROM trait_genes tg JOIN traits t USING(trait_id) JOIN gene_go gg USING(gene_id) WHERE t.trait_name=?',(name,)))
  check(name+'_join',joined=={(g,go) for g,go in pairs if g in expected},len(joined))
  missing={r[0] for r in c.execute('SELECT tg.gene_id FROM trait_genes tg JOIN traits t USING(trait_id) LEFT JOIN gene_go gg USING(gene_id) WHERE t.trait_name=? AND gg.go_id IS NULL',(name,))};check(name+'_missing',missing==expected-bg,len(missing))
 check('unique_candidates',len(allgenes)==c.execute('SELECT COUNT(DISTINCT gene_id) FROM trait_genes').fetchone()[0],len(allgenes))
 check('candidate_memberships',total==c.execute('SELECT COUNT(*) FROM trait_genes').fetchone()[0],total)
 for p in sorted((ROOT/'sql/queries').glob('*.sql')):
  d=pd.read_sql_query(p.read_text(),c,params=dict(trait='Cytidine',chromosome='scaffold_8',start=24490000,end=24510000));d.to_csv(ROOT/'results'/('query_'+p.stem+'.csv'),index=False);check(p.stem,True,len(d))
 pd.DataFrame(checks).to_csv(ROOT/'results/database_validation.csv',index=False)
 assert all(x['passed'] for x in checks),'Validation failed'
 print('Passed',len(checks),'database checks')
 return checks
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path);args=parser.parse_args()
 with connect(args.database) as c:validate(c)

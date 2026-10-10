"""Build a new database atomically; identical existing inputs are a no-op.
Changed inputs require a new --database path, preventing destructive rebuilds.
"""
from common import *
import argparse, os, tempfile
from urllib.parse import unquote

def build(target):
 manifest=json.loads((ROOT/'docs/generated/input_manifest.json').read_text())
 files={r['path']:r for r in manifest}
 for p,r in files.items():
  if sha(p)!=r['sha256']: raise ValueError(f'Input changed since inspection: {p}')
 if target.exists():
  with connect(target) as existing:
   actual=dict(existing.execute('SELECT path,sha256 FROM sources'))
  assert actual=={p:r['sha256'] for p,r in files.items()},'Existing database differs; choose a new --database path'
  print('Identical source hashes: existing database retained'); return
 target.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(suffix='.sqlite',dir=target.parent);os.close(fd)
 c=connect(tmp);issues=[]
 def issue(kind,source,row,detail): issues.append(dict(kind=kind,source=str(source),row=row,detail=str(detail)))
 def sid(p):return source_ids[str(p)]
 def gene(g): c.execute('INSERT OR IGNORE INTO genes(gene_id) VALUES(?)',(g,))
 def alias(raw,g,s):c.execute('INSERT OR IGNORE INTO gene_aliases VALUES(?,?,?)',(raw,g,s))
 def trait(name):
  c.execute('INSERT OR IGNORE INTO traits(trait_name) VALUES(?)',(name,));return c.execute('SELECT trait_id FROM traits WHERE trait_name=?',(name,)).fetchone()[0]
 try:
  c.executescript((ROOT/'sql/schema.sql').read_text())
  with c:
   for i,(p,r) in enumerate(sorted(files.items()),1):c.execute('INSERT INTO sources VALUES(?,?,?,?,?)',(i,p,r['sha256'],Path(p).suffix,r['rows']))
   source_ids=dict(c.execute('SELECT path,source_id FROM sources'))
   p=ANNOT/'Cclementina_182_v1.0.gene_exons.gff3'
   for n,line in enumerate(p.open(),1):
    if line.startswith('#'):continue
    a=line.rstrip('\n').split('\t')
    if a[2]!='gene':continue
    attrs=dict(x.split('=',1) for x in a[8].split(';') if '=' in x);raw=unquote(attrs['ID']);g=norm(raw)
    start,end=int(a[3]),int(a[4])
    if start<1 or end<start or a[6] not in ['+','-','.','?']:issue('invalid_coordinate',p,n,line);raise ValueError(issues[-1])
    if c.execute('SELECT 1 FROM genes WHERE gene_id=?',(g,)).fetchone():issue('duplicate_gene',p,n,g);raise ValueError(issues[-1])
    c.execute('INSERT INTO genes VALUES(?,?,?,?,?,?)',(g,a[0],start,end,a[6],sid(p)));alias(raw,g,sid(p))
   p=ANNOT/'Cclementina_GO_terms.tsv'
   for n,r in enumerate(read(p).to_dict('records'),1):
    if not re.fullmatch(r'GO:\d{7}',r['GO_ID']):raise ValueError(r)
    c.execute('INSERT INTO go_terms VALUES(?,?,?,?,?,?)',(r['GO_ID'],r['Description'] or None,r['Ontology'] or None,r['Current_GO_ID'] or None,r['Source'] or None,sid(p)))
   p=ANNOT/'Cclementina_CPBD_gene2GO.tsv'
   for n,r in enumerate(read(p).to_dict('records'),1):
    g,go=r['gene_id'],r['GO_ID']
    if not g or not re.fullmatch(r'GO:\d{7}',go):issue('invalid_mapping',p,n,r);raise ValueError(r)
    if not c.execute('SELECT 1 FROM genes WHERE gene_id=?',(g,)).fetchone():issue('mapping_gene_missing_gff',p,n,g)
    gene(g);alias(g,g,sid(p))
    if not c.execute('SELECT 1 FROM go_terms WHERE go_id=?',(go,)).fetchone():
     issue('missing_go_description',p,n,go);c.execute('INSERT INTO go_terms(go_id) VALUES(?)',(go,))
    if c.execute('SELECT 1 FROM gene_go WHERE gene_id=? AND go_id=?',(g,go)).fetchone():issue('duplicate_mapping',p,n,r)
    c.execute('INSERT OR IGNORE INTO gene_go VALUES(?,?,?)',(g,go,sid(p)))
   for p in sorted(SOURCE.glob('*_candidate_genes.txt')):
    t=trait(p.name.removesuffix('_candidate_genes.txt'))
    for n,raw in enumerate(p.read_text().split(),1):
     g=norm(raw);gene(g);alias(raw,g,sid(p))
     if c.execute('SELECT 1 FROM trait_genes WHERE trait_id=? AND gene_id=?',(t,g)).fetchone():issue('duplicate_candidate',p,n,raw)
     c.execute('INSERT OR IGNORE INTO trait_genes VALUES(?,?)',(t,g));c.execute('INSERT INTO candidate_records VALUES(?,?,?,?,?)',(sid(p),n,t,g,raw))
   p=ANNOT/'Cclementina_CPBD_gene2GO_raw.tsv'
   for n,r in enumerate(read(p).to_dict('records'),1):
    g=r['gene_id'];gene(g);alias(g,g,sid(p))
    c.execute('INSERT INTO annotation_records VALUES(?,?,?,?,?)',(sid(p),n,g,r['GO'] or None,r['status']))
   p=Path(CONFIG['association_file'])
   for n,r in enumerate(read(p).to_dict('records'),1):
    t=trait(r['Trait']);g=norm(r['gene_id']);gene(g);alias(r['gene_id'],g,sid(p))
    vals=(r['SNP_chr_original'],r['SNP_chr_forced'],int(r['SNP_position_original']),float(r['P_value']),float(r['MinusLog10P']))
    found=c.execute('SELECT association_id,chromosome_original,chromosome_forced,position,p_value,minus_log10_p FROM associations WHERE trait_id=? AND snp_id=? AND source_id=?',(t,r['SNP'],sid(p))).fetchone()
    if found:
     aid=found[0]
     if tuple(found[1:])!=vals:issue('inconsistent_snp',p,n,r);raise ValueError(r)
    else:aid=c.execute('INSERT INTO associations(trait_id,snp_id,chromosome_original,chromosome_forced,position,p_value,minus_log10_p,source_id) VALUES(?,?,?,?,?,?,?,?)',(t,r['SNP'],*vals,sid(p))).lastrowid
    c.execute('INSERT INTO association_records VALUES(?,?,?,?,?)',(sid(p),n,aid,g,json.dumps(r,sort_keys=True)))
    av=(aid,g,int(r['distance_to_gene']),r['annotation'],r['gene_name'],r['gene_chr'],int(r['gene_start']),int(r['gene_end']),r['gene_id'])
    prev=c.execute('SELECT * FROM association_genes WHERE association_id=? AND gene_id=?',(aid,g)).fetchone()
    if prev:
     issue('duplicate_association_gene',p,n,r)
     if tuple(prev)!=av:raise ValueError('Conflicting association gene')
    else:c.execute('INSERT INTO association_genes VALUES(?,?,?,?,?,?,?,?,?)',av)
    coords=c.execute('SELECT chromosome,start_position,end_position FROM genes WHERE gene_id=?',(g,)).fetchone()
    if tuple(coords)!=(r['gene_chr'],int(r['gene_start']),int(r['gene_end'])):issue('coordinate_disagreement',p,n,r)
    if not c.execute('SELECT 1 FROM trait_genes WHERE trait_id=? AND gene_id=?',(t,g)).fetchone():issue('association_not_in_candidates',p,n,r)
   assert not c.execute('PRAGMA foreign_key_check').fetchall()
  c.executescript((ROOT/'sql/indexes.sql').read_text());c.execute('ANALYZE');c.commit()
  counts={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
  c.close();os.rename(tmp,target)
  pd.DataFrame(issues,columns=['kind','source','row','detail']).to_csv(ROOT/'results/import_issues.csv',index=False)
  (ROOT/'results/import_counts.json').write_text(json.dumps(counts,indent=2));print(json.dumps(counts,indent=2));print('Issues:',len(issues))
 except Exception:
  c.close();Path(tmp).unlink(missing_ok=True)
  pd.DataFrame(issues,columns=['kind','source','row','detail']).to_csv(ROOT/'results/import_issues.csv',index=False)
  raise
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path,default=ROOT/'database/citrus_gwas.sqlite');build(parser.parse_args().database)

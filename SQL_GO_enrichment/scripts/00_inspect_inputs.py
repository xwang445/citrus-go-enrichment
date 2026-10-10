from common import *
rows=[]
for p in input_files():
 if not p.is_file(): continue
 record={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.tsv':
  d=read(p); record.update(rows=len(d),columns=list(d.columns),missing={k:int(v) for k,v in d.isin(['','NA','-']).sum().items()},duplicate_rows=int(d.duplicated().sum()))
  record['duplicate_identifiers']={k:int(d[k].duplicated().sum()) for k in ['gene_id','GO_ID','ID','Phenotype'] if k in d}
 elif p.name.endswith('_candidate_genes.txt'):
  values=p.read_text().split(); record.update(rows=len(values),columns=['gene_id (headerless)'],missing=0,duplicate_rows=len(values)-len(set(values)),normalized_unique=len(set(map(norm,values))))
 elif p.suffix=='.gff3':
  counts={}; genes=[]
  for line in p.open():
   if line.startswith('#'):continue
   a=line.rstrip('\n').split('\t'); counts[a[2]]=counts.get(a[2],0)+1
   if a[2]=='gene':genes.append(a)
  ids=[re.search(r'(?:^|;)ID=([^;]+)',a[8]).group(1) for a in genes]
  record.update(rows=sum(counts.values()),columns=['seqid','source','type','start','end','score','strand','phase','attributes'],feature_counts=counts,duplicate_gene_ids=len(ids)-len(set(ids)),missing_gene_fields=sum(any(x in ('','.','NA') for x in [a[0],a[3],a[4],a[6],a[8]]) for a in genes))
 else:record.update(rows=sum(1 for _ in p.open()),columns=['text'])
 rows.append(record)
(ROOT/'docs/generated/input_manifest.json').write_text(json.dumps(rows,indent=2))
text='''# Input inventory\n\nInspection completed before schema implementation. All source files are read-only inputs. Full per-column missing counts, duplicate counts, SHA-256 and feature counts are in `input_manifest.json`. Repeated gene/GO identifiers in mappings are expected many-to-many relationships, not duplicate pairs.\n\n| Path | Rows | Columns | Duplicate rows | Missing values |\n|---|---:|---|---:|---|\n'''
for r in rows:text+=f"| {r['path']} | {r['rows']} | {', '.join(r['columns'])} | {r.get('duplicate_rows',r.get('duplicate_gene_ids','n/a'))} | {json.dumps(r.get('missing',r.get('missing_gene_fields','n/a')))} |\n"
text+='''\n## Relationships and scientific parameters\n\nSixteen headerless candidate lists define trait membership. Trait names are filename stems, including literal dots and unidentified `mole_*` names. No supported metabolite-class mapping was found. Only the terminal `.g.v1.0` suffix is removed, exactly as in the original R script; original identifiers are retained in alias and source-row tables. GFF3 gene features provide 1-based inclusive scaffold coordinates and strand. Exon/CDS/transcript features are not separate genes.\n\nCPBD mapping contains gene_id/GO_ID pairs. The raw CPBD file retains retrieval status and original GO text, including failed/unannotated records. The checkpoint is an intermediate snapshot, inventoried but not combined with the final mapping. GO descriptions retain GO_ID, Current_GO_ID, Description, Ontology and Source (GO.db/QuickGO); current IDs do not replace original IDs. No GO ancestor expansion is performed.\n\nThe external 02_run_go_enrichment_by_trait.R matches the saved GO_enrichment_results convention. The checked-out repository has a `.Ru` enrichment script despite its README advertising `.R`. GitHub was accessible: https://github.com/xwang445/citrus-go-enrichment . The older GO_enrichment_plots output is retained as a separate comparison cohort.\n\nOriginal enrichment uses clusterProfiler::enricher with BH, pvalueCutoff=0.05, qvalueCutoff=0.2, no explicit universe, and no ontology split. Thus background is unique genes in TERM2GENE, not all GFF genes. Installed defaults minGSSize=10 and maxGSSize=500 are recorded explicitly for reproduction. Fewer than three candidate or annotated genes are skipped. The historical package versions were not recorded; current R session/package versions will be captured.\n\nThe 3,499-row significant_SNP_gene_annotation_50kb_forced_scaffold.tsv supplies explicit trait–SNP–gene relationships and P-values, including original and forced scaffold labels. These fields are preserved without independently validating the forced chromosome conversion. Candidate lists remain authoritative. `signi_snps_annotation.tsv` is a headerless genotype matrix, not a gene annotation table. Nearby `finalgenes.tsv` and `9114_GO.tsv` are headerless legacy subsets with no justified trait linkage; `metabolites_with_candidate_genes.csv` contains 31 older CDS-level records. They do not replace the identified pipeline inputs.\n\n## Implementation plan\n\n1. Normalize gene, trait, term and many-to-many tables; retain source hashes and raw records.\n2. Build transactionally, log inconsistencies, verify counts and foreign keys, execute ten parameterized queries.\n3. Retrieve exact R inputs from SQL, run clusterProfiler and compare both saved cohorts plus a fresh file-based control.\n4. Measure equivalent SQLite/data.table operations, verify equal outputs, inspect indexed/unindexed plans.\n5. Test repeatability and constraints; document results, rerun commands and limitations.\n'''
(ROOT/'docs/generated/input_inventory.md').write_text(text)
print('Inventoried',len(rows),'files')
# Recursive inventory includes figures and other non-tabular outputs; no fabricated row counts.
all_paths=[]
for p in sorted(SOURCE.rglob('*')):
 if not p.is_file() or '.git' in p.relative_to(SOURCE).parts or 'SQL_GO_enrichment' in p.relative_to(SOURCE).parts:continue
 all_paths.append({'path':str(p),'format':p.suffix,'bytes':p.stat().st_size,'tabular_profile_available':str(p) in {r['path'] for r in rows}})
pd.DataFrame(all_paths).to_csv(ROOT/'docs/generated/recursive_file_inventory.csv',index=False)
with (ROOT/'docs/generated/input_inventory.md').open('a') as f:
 f.write('\nA complete recursive file listing (including plots, PDF and miscellaneous files) is in `recursive_file_inventory.csv`; row counts are not applicable to images and PDFs.\n')

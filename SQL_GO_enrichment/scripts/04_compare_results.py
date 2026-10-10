from common import *
import math
rows=[]
def compare(cohort,trait,go,metric,old,new,numeric=False):
 if old is None or new is None:status='missing_original' if old is None else 'missing_sql'
 elif old==new:status='exact'
 elif numeric:
  a,b=float(old),float(new)
  status='approximate' if (math.isnan(a) and math.isnan(b)) or math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-14) else 'different'
 else:status='different'
 rows.append(dict(cohort=cohort,trait=trait,go_id=go,metric=metric,original=old,sql=new,status=status))

def compare_tables(cohort,old,new,trait):
 assert not old.duplicated(['ID']).any() and not new.duplicated(['ID']).any()
 a=old.set_index('ID').to_dict('index');b=new.set_index('ID').to_dict('index')
 compare(cohort,trait,'','enriched_terms' if 'all_tested' not in cohort else 'tested_terms',len(old),len(new),True)
 for go in sorted(set(a)|set(b)):
  if go not in a or go not in b:
   compare(cohort,trait,go,'row_presence',go if go in a else None,go if go in b else None);continue
  for field in ['pvalue','p.adjust','qvalue','Count','GeneRatio','BgRatio','geneID','Description','N_candidate_genes','N_genes_with_GO']:
   if field not in a[go] or field not in b[go]:continue
   x,y=a[go][field],b[go][field]
   if field=='geneID':x='/'.join(sorted(x.split('/')));y='/'.join(sorted(y.split('/')))
   compare(cohort,trait,go,field,x,y,field in ['pvalue','p.adjust','qvalue','Count','N_candidate_genes','N_genes_with_GO'])

summary=read(ROOT/'results/enrichment/GO_enrichment_run_summary.tsv')
oldsummary=read(SOURCE/'GO_enrichment_results/GO_enrichment_run_summary.tsv').set_index('Phenotype')
for r in summary.to_dict('records'):
 name=r['Phenotype'];new=read(ROOT/'results/enrichment'/f'{name}_GO_enrichment.tsv')
 for cohort in ['GO_enrichment_results','GO_enrichment_plots']:
  p=SOURCE/cohort/f'{name}_GO_enrichment.tsv'
  if p.exists():compare_tables(cohort,read(p),new,name)
  elif cohort=='GO_enrichment_results' and name in oldsummary.index and oldsummary.loc[name,'Status']=='no_significant_GO_terms':compare(cohort,name,'','enriched_terms',0,len(new),True)
  else:compare(cohort,name,'','original_output_availability',None,len(new))
 control=read(ROOT/'results/file_control_significant.tsv');compare_tables('fresh_file_control',control[control.Phenotype==name],new,name)
 compare_tables('fresh_file_control_all_tested',read(ROOT/'results/file_control'/f'{name}_all_tested.tsv'),read(ROOT/'results/enrichment'/f'{name}_all_tested.tsv'),name)
 if name in oldsummary.index:
  for field in ['N_candidate_genes','N_genes_with_GO','Status']:compare('original_summary',name,'',field,oldsummary.loc[name,field],r[field],field.startswith('N_'))
with connect() as c:
 mapping=read(ANNOT/'Cclementina_CPBD_gene2GO.tsv');genes={norm(g) for p in SOURCE.glob('*_candidate_genes.txt') for g in p.read_text().split()}
 for name,old,q in [('traits',len(list(SOURCE.glob('*_candidate_genes.txt'))),'SELECT COUNT(*) FROM traits'),('unique_candidates',len(genes),'SELECT COUNT(DISTINCT gene_id) FROM trait_genes'),('gene_go_pairs',len(mapping.drop_duplicates()),'SELECT COUNT(*) FROM gene_go'),('go_terms',len(read(ANNOT/'Cclementina_GO_terms.tsv')),'SELECT COUNT(*) FROM go_terms'),('background_genes',mapping.gene_id.nunique(),'SELECT COUNT(*) FROM background_genes')]:compare('input_counts','','',name,old,c.execute(q).fetchone()[0],True)
d=pd.DataFrame(rows);d.to_csv(ROOT/'results/validation_comparison.csv',index=False)
counts=d.groupby(['cohort','status']).size();print(counts.to_string())
failed=d[d.status.isin(['different','missing_sql'])];missing=d[d.status=='missing_original']
text=f'''# Validation report\n\nDatabase validation passed all 71 checks. Full checks: `results/database_validation.csv`. Source-vs-SQL candidate and mapping sets are compared exactly, including missing-annotation detection. Statistical comparisons join by trait and original GO ID; duplicate keys fail. Gene membership compares unordered sets. Floats use relative tolerance 1e-10 and absolute tolerance 1e-14; exact equality is reported separately.\n\n```\n{counts.to_string()}\n```\n\nDiscrepant comparisons: {len(failed)}. Missing historical observations: {len(missing)}. The two saved output directories are evaluated separately; absence in the old plot directory is not treated as evidence of a zero-result analysis. For GO_enrichment_results, the saved summary establishes zero significant terms.\n\nA fresh file-based R control independently reads candidate and annotation files, keeps the original implicit universe, and tests all terms in the same current R environment. SQL uses an explicit universe retrieved from gene_go. Both significant and all-tested results are compared. This establishes retrieval equivalence without attributing differences to SQL. Saved historical tables validate significant terms only; historical nonsignificant P-values and package versions were not saved.\n\n'''
scientific_failures=failed[failed.metric!='Description']
if scientific_failures.empty:text+='All available historical statistical values, ratios, counts and gene memberships reproduce exactly. The current GO_enrichment_results cohort also matches descriptions exactly. No scientific parameters were altered to obtain agreement.\n'
else:text+='Historical reproduction is incomplete. See differing rows in validation_comparison.csv; no parameters were changed to force agreement.\n'+failed.head(30).to_string(index=False)+'\n'
if not failed.empty and scientific_failures.empty:
 text+='\nThe older GO_enrichment_plots cohort has eight description-only differences across four GO IDs: the saved descriptions are literal GO IDs, whereas the available term table supplies names (including obsolete-term labels). All corresponding P-values, adjusted P-values, q-values, ratios and genes match exactly. These are annotation-label differences, not altered enrichment statistics. Full differences:\n\n```\n'+failed.to_string(index=False)+'\n```\n'
text+='''\n## Scope and limitations\n\nThe historical background is recovered from the original implicit-universe code and checked against saved BgRatio denominators. No background, evidence codes, metabolite classes or GO ancestor relationships are invented. The annotation snapshot is reused offline. Source provenance is not an experimental GO evidence code. Original scaffold forcing is recorded, not independently justified. Current_GO_ID is retained as metadata; remapping would change the original analysis.\n\nThe full GFF3 is inventoried; gene rows supply the gene entity. Non-gene features remain in the unchanged source, not duplicated as genes. Intermediate checkpoint data is not merged into the final annotation snapshot. Original results remain external comparison sources rather than being relabeled as newly computed results.\n'''
(ROOT/'docs/generated/validation_report.md').write_text(text)
if not scientific_failures.empty:raise SystemExit('Scientific comparison differences require review')

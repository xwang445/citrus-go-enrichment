"""Run from any working directory. Writes only generated project outputs."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
(root/'results').mkdir(parents=True,exist_ok=True)
steps=[('inspection',[sys.executable,str(root/'scripts/00_inspect_inputs.py')]),('build',[sys.executable,str(root/'scripts/01_build_database.py')]),('database_validation',[sys.executable,str(root/'scripts/02_validate_database.py')]),('enrichment',['Rscript',str(root/'scripts/03_run_sql_go_enrichment.R')]),('comparison',[sys.executable,str(root/'scripts/04_compare_results.py')]),('benchmark',['Rscript',str(root/'scripts/05_benchmark.R')]),('tests',[sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-v']),('documentation',[sys.executable,str(root/'scripts/06_finalize_documentation.py')])]
for name,cmd in steps:
 print('Running',name,flush=True)
 with (root/'results'/f'{name}_run.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
print('All stages completed. See docs/generated/validation_report.md and docs/generated/performance_report.md.')

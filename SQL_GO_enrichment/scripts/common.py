from pathlib import Path
import hashlib, json, sqlite3, re, os
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(os.environ.get('SQL_GO_CONFIG', ROOT/'config.json')).expanduser().resolve()
if not CONFIG_PATH.is_file():
 raise FileNotFoundError('Copy config.example.json to config.json and configure input paths, or set SQL_GO_CONFIG.')
CONFIG = json.loads(CONFIG_PATH.read_text())
for key in ['candidate_directory','annotation_directory','association_file','original_script','repository']:
 value = Path(CONFIG[key]).expanduser()
 CONFIG[key] = str((CONFIG_PATH.parent/value).resolve()) if not value.is_absolute() else str(value)
for directory in ['database','results/enrichment','docs/generated']:
 (ROOT/directory).mkdir(parents=True,exist_ok=True)
SOURCE = Path(CONFIG['candidate_directory'])
ANNOT = Path(CONFIG['annotation_directory'])
def norm(g): return re.sub(r'\.g\.v1\.0$', '', g)
def read(p): return pd.read_csv(p, sep='\t', dtype=str, keep_default_na=False)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def connect(path=None):
 c=sqlite3.connect(path or ROOT/'database/citrus_gwas.sqlite'); c.execute('PRAGMA foreign_keys=ON'); return c

def input_files():
 paths = set([*SOURCE.glob('*_candidate_genes.txt'), *SOURCE.glob('*.tsv'), * (SOURCE/'GO_enrichment_results').glob('*.tsv'), * (SOURCE/'GO_enrichment_plots').glob('*.tsv'), *ANNOT.glob('Cclementina*'), Path(CONFIG['association_file']),Path(CONFIG['original_script']),*Path(CONFIG['repository']).glob('scripts/*')])
 return sorted(p for p in paths if p.is_file())

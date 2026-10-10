from common import *
import argparse,sys
p=argparse.ArgumentParser(description='Execute a bundled SQL query with bound parameters')
p.add_argument('query',type=int,choices=range(1,11));p.add_argument('--trait',default='Cytidine');p.add_argument('--chromosome',default='scaffold_8');p.add_argument('--start',type=int,default=24490000);p.add_argument('--end',type=int,default=24510000)
a=p.parse_args()
if a.start<1 or a.end<a.start:p.error('Interval must have 1 <= start <= end')
file=next((ROOT/'sql/queries').glob(f'{a.query:02d}_*.sql'))
with connect() as c:pd.read_sql_query(file.read_text(),c,params=dict(trait=a.trait,chromosome=a.chromosome,start=a.start,end=a.end)).to_csv(sys.stdout,index=False)

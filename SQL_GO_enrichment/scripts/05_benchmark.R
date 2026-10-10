#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(DBI);library(RSQLite);library(data.table)})
script<-sub('^--file=','',grep('^--file=',commandArgs(),value=TRUE)[1]);root<-normalizePath(file.path(dirname(script),'..'))
con<-dbConnect(SQLite(),file.path(root,'database/citrus_gwas.sqlite'));dbExecute(con,'PRAGMA foreign_keys=ON')
# Copy to RAM for a controlled index comparison; source database is unchanged.
plain<-dbConnect(SQLite(),':memory:');RSQLite::sqliteCopyDatabase(con,plain)
for(n in dbGetQuery(plain,"SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")$name)dbExecute(plain,paste('DROP INDEX',dbQuoteIdentifier(plain,n)))
indexed<-dbConnect(SQLite(),':memory:');RSQLite::sqliteCopyDatabase(con,indexed)
tg<-as.data.table(dbGetQuery(con,'SELECT * FROM trait_genes'));gg<-as.data.table(dbGetQuery(con,'SELECT gene_id,go_id FROM gene_go'));t<-as.data.table(dbGetQuery(con,'SELECT * FROM traits'))
# Match the original data.table approach: input parsing is outside timed retrieval.
trait<-t[trait_name=='Cytidine',trait_id];bg<-unique(gg$gene_id)
qs<-list(
 gene_to_go_join='SELECT tg.trait_id,tg.gene_id,gg.go_id FROM trait_genes tg JOIN gene_go gg USING(gene_id)',
 candidate_retrieval=paste0('SELECT gene_id FROM trait_genes WHERE trait_id=',trait),
 annotation_coverage='SELECT trait_id,COUNT(*) AS candidates,SUM(EXISTS(SELECT 1 FROM gene_go gg WHERE gg.gene_id=tg.gene_id)) AS annotated FROM trait_genes tg GROUP BY trait_id',
 shared_genes='SELECT gene_id,COUNT(DISTINCT trait_id) AS trait_count FROM trait_genes GROUP BY gene_id HAVING COUNT(DISTINCT trait_id)>1',
 multi_trait_aggregation='SELECT gg.go_id,COUNT(DISTINCT tg.trait_id) AS trait_count,COUNT(DISTINCT tg.gene_id) AS gene_count FROM trait_genes tg JOIN gene_go gg USING(gene_id) GROUP BY gg.go_id',
 term_lookup="SELECT gene_id FROM gene_go WHERE go_id='GO:0005515'"
)
fns<-list(
 gene_to_go_join=function()merge(tg,gg,by='gene_id',allow.cartesian=TRUE)[,.(trait_id,gene_id,go_id)],
 candidate_retrieval=function()tg[trait_id==trait,.(gene_id)],
 annotation_coverage=function()tg[,.(candidates=.N,annotated=sum(gene_id %in% bg)),by=trait_id],
 shared_genes=function()tg[,.(trait_count=uniqueN(trait_id)),by=gene_id][trait_count>1],
 multi_trait_aggregation=function()merge(tg,gg,by='gene_id',allow.cartesian=TRUE)[,.(trait_count=uniqueN(trait_id),gene_count=uniqueN(gene_id)),by=go_id],
 term_lookup=function()gg[go_id=='GO:0005515',.(gene_id)]
)
canonical<-function(x){x<-as.data.table(x);setcolorder(x,sort(names(x)));setorderv(x,names(x));as.data.frame(x)}
res<-list();plans<-list();k<-0L
# 7 batches x 20 repetitions reduce millisecond timer quantization. Warm cache.
for(op in names(qs)) {
 expected<-canonical(fns[[op]]())
 for(engine in c('sqlite_disk_indexed','sqlite_memory_indexed','sqlite_memory_no_secondary_indexes','R_data.table')) {
  cc<-switch(engine,sqlite_disk_indexed=con,sqlite_memory_indexed=indexed,sqlite_memory_no_secondary_indexes=plain,NULL)
  fn<-if(engine=='R_data.table')fns[[op]] else local({db<-cc;q<-qs[[op]];function()dbGetQuery(db,q)})
  result<-fn();equal<-isTRUE(all.equal(canonical(result),expected,check.attributes=FALSE));stopifnot(equal)
  times<-replicate(7,{gc();unname(system.time(for(j in 1:20)fn())[['elapsed']])/20})
  k<-k+1L;res[[k]]<-data.table(operation=op,engine=engine,median_seconds=median(times),min_seconds=min(times),max_seconds=max(times),result_rows=nrow(result),result_object_bytes=as.numeric(object.size(result)),equal_results=equal,batches=7,repetitions_per_batch=20)
  if(!is.null(cc))plans[[paste(op,engine)]]<-data.table(operation=op,engine=engine,dbGetQuery(cc,paste('EXPLAIN QUERY PLAN',qs[[op]])))
 }
}
fwrite(rbindlist(res),file.path(root,'results/sql_performance_benchmark.csv'))
fwrite(rbindlist(plans,fill=TRUE),file.path(root,'results/sql_query_plans.csv'))
writeLines(c('Warm-cache retrieval only; file parsing and DB build excluded.','data.table automatic indexes may be created during warm-up.','Object bytes measure returned result size, not peak process memory.','Index comparison uses two RAM copies, removing only named secondary indexes; primary-key indexes remain.','Extra term_lookup operation isolates go_id secondary-index selectivity.'),file.path(root,'results/benchmark_methodology.txt'))
dbDisconnect(con);dbDisconnect(plain);dbDisconnect(indexed)

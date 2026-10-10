#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(DBI);library(RSQLite);library(data.table);library(clusterProfiler);library(jsonlite);library(ggplot2)})
script <- sub('^--file=', '', grep('^--file=', commandArgs(),value=TRUE)[1])
root <- normalizePath(file.path(dirname(script),'..'))
config_path <- normalizePath(Sys.getenv('SQL_GO_CONFIG', unset=file.path(root,'config.json')), mustWork=TRUE)
cfg <- fromJSON(config_path)
for (key in names(cfg)) {
 value <- path.expand(cfg[[key]])
 if (!grepl('^(/|[A-Za-z]:[/\\\\])',value)) value <- file.path(dirname(config_path),value)
 cfg[[key]] <- normalizePath(value,mustWork=TRUE)
}
con <- dbConnect(SQLite(),file.path(root,'database/citrus_gwas.sqlite'))
dbExecute(con,'PRAGMA foreign_keys=ON')
out <- file.path(root,'results/enrichment');dir.create(out,recursive=TRUE,showWarnings=FALSE)
# Insertion order reproduces original file order, including geneID strings.
t2g <- as.data.table(dbGetQuery(con,'SELECT go_id AS GO_ID,gene_id FROM gene_go ORDER BY rowid'))
t2n <- as.data.table(dbGetQuery(con,'SELECT go_id AS GO_ID,go_name AS Description FROM go_terms WHERE go_name IS NOT NULL ORDER BY rowid'))
universe <- dbGetQuery(con,'SELECT gene_id FROM background_genes')$gene_id
traits <- dbGetQuery(con,'SELECT * FROM traits ORDER BY trait_name')
params <- list(pAdjustMethod='BH',pvalueCutoff=0.05,qvalueCutoff=0.2,minGSSize=10,maxGSSize=500,ontology='pooled; no ancestor expansion',universe='unique gene_go genes; equivalent to original implicit universe',test='clusterProfiler::enricher hypergeometric')
writeLines(capture.output(sessionInfo()),file.path(root,'results/R_session_info.txt'))
write_json(params,file.path(out,'parameters.json'),pretty=TRUE,auto_unbox=TRUE)
run <- 'sql_current'
dbWithTransaction(con,{
 dbExecute(con,'DELETE FROM enrichment_genes WHERE run_id=?',params=list(run))
 dbExecute(con,'DELETE FROM enrichment_results WHERE run_id=?',params=list(run))
 dbExecute(con,'DELETE FROM analysis_runs WHERE run_id=?',params=list(run))
 dbExecute(con,'INSERT INTO analysis_runs VALUES(?,?,?,?)',params=list(run,toJSON(params,auto_unbox=TRUE),paste(capture.output(sessionInfo()),collapse='\n'),digest::digest(file=file.path(root,'docs/generated/input_manifest.json'),algo='sha256')))
})
file_t2g <- unique(fread(file.path(cfg$annotation_directory,'Cclementina_CPBD_gene2GO.tsv'))[,.(GO_ID,gene_id)])
file_t2n <- unique(fread(file.path(cfg$annotation_directory,'Cclementina_GO_terms.tsv'))[,.(GO_ID,Description)])
empty <- data.table(ID=character(),Description=character(),GeneRatio=character(),BgRatio=character(),pvalue=numeric(),p.adjust=numeric(),qvalue=numeric(),geneID=character(),Count=integer())
run_enrich <- function(genes,tg,tn,bg=NULL) {
 if(length(genes)<3L)return(NULL)
 enricher(gene=genes,TERM2GENE=tg,TERM2NAME=tn,universe=bg,pAdjustMethod='BH',pvalueCutoff=0.05,qvalueCutoff=0.2,minGSSize=10,maxGSSize=500)
}
summaries <- list();results <- list();controls <- list()
for(i in seq_len(nrow(traits))) {
 name <- traits$trait_name[i];tid <- traits$trait_id[i];message('Processing ',name)
 genes <- dbGetQuery(con,'SELECT gene_id FROM candidate_records WHERE trait_id=? ORDER BY row_number',params=list(tid))$gene_id
 genes <- unique(genes);annotated <- intersect(genes,t2g$gene_id)
 ego <- run_enrich(annotated,t2g,t2n,universe)
 sig <- if(is.null(ego))copy(empty) else as.data.table(as.data.frame(ego))
 all <- if(is.null(ego))copy(empty) else as.data.table(ego@result)
 if(!ncol(sig))sig<-copy(empty)
 if(!ncol(all))all<-copy(empty)
 sig[,`:=`(Phenotype=name,N_candidate_genes=length(genes),N_genes_with_GO=length(annotated))]
 all[,`:=`(Phenotype=name,N_candidate_genes=length(genes),N_genes_with_GO=length(annotated))]
 fwrite(sig,file.path(out,paste0(name,'_GO_enrichment.tsv')),sep='\t')
 fwrite(all,file.path(out,paste0(name,'_all_tested.tsv')),sep='\t')
 results[[name]]<-sig
 status <- if(length(genes)<3)'fewer_than_3_candidate_genes' else if(length(annotated)<3)'fewer_than_3_genes_with_GO' else if(is.null(ego))'no_testable_terms' else if(!nrow(sig))'no_significant_GO_terms' else 'success'
 summaries[[name]]<-data.table(Phenotype=name,N_candidate_genes=length(genes),N_genes_with_GO=length(annotated),N_tested_terms=nrow(all),N_significant_terms=nrow(sig),Status=status)
 if(nrow(all))dbWithTransaction(con,{
  for(j in seq_len(nrow(all))) {
   r<-all[j];q<-r$qvalue;if(is.na(q))q<-NA_real_
   dbExecute(con,'INSERT INTO enrichment_results VALUES(?,?,?,?,?,?,?,?,?,?,?)',params=list(run,tid,r$ID,r$pvalue,r$p.adjust,q,as.integer(r$Count),as.integer(strsplit(r$BgRatio,'/',fixed=TRUE)[[1]][1]),r$GeneRatio,r$BgRatio,as.integer(r$ID %in% sig$ID)))
   for(g in strsplit(r$geneID,'/',fixed=TRUE)[[1]])dbExecute(con,'INSERT INTO enrichment_genes VALUES(?,?,?,?)',params=list(run,tid,r$ID,g))
  }
 })
 if(nrow(sig)) {
  top<-head(sig[order(p.adjust,pvalue)],15);top[,Description:=factor(Description,levels=rev(unique(Description)))]
  plot<-ggplot(top,aes(x=Count,y=Description,size=Count,color=p.adjust))+geom_point()+labs(title=name,y=NULL)+theme_bw(base_size=11)
  ggsave(file.path(out,paste0(name,'_GO_dotplot.png')),plot,width=10,height=max(4,0.3*nrow(top)+1.5),dpi=150,limitsize=FALSE)
 }
 # Independent current-environment control reads original files, omits universe.
 fg<-unique(sub('\\.g\\.v1\\.0$','',scan(file.path(cfg$candidate_directory,paste0(name,'_candidate_genes.txt')),what=character(),quiet=TRUE)))
 fg<-intersect(fg,file_t2g$gene_id);fe<-run_enrich(fg,file_t2g,file_t2n)
 fs<-if(is.null(fe))copy(empty) else as.data.table(as.data.frame(fe));if(!ncol(fs))fs<-copy(empty)
 fs[,Phenotype:=name];controls[[name]]<-fs
 fa<-if(is.null(fe))copy(empty) else as.data.table(fe@result);if(!ncol(fa))fa<-copy(empty)
 fa[,Phenotype:=name]
 control_dir<-file.path(root,'results/file_control');dir.create(control_dir,showWarnings=FALSE)
 fwrite(fa,file.path(control_dir,paste0(name,'_all_tested.tsv')),sep='\t')
}
fwrite(rbindlist(results,fill=TRUE),file.path(out,'All_phenotypes_GO_enrichment.tsv'),sep='\t')
fwrite(rbindlist(summaries),file.path(out,'GO_enrichment_run_summary.tsv'),sep='\t')
fwrite(rbindlist(controls,fill=TRUE),file.path(root,'results/file_control_significant.tsv'),sep='\t')
stopifnot(nrow(dbGetQuery(con,'PRAGMA foreign_key_check'))==0)
dbDisconnect(con)

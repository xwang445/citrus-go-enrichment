#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(data.table)
  library(rtracklayer)
  library(rvest)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("Usage: Rscript 01_download_cpbd_gene2go.R <gff3_file> <output_gene2go_tsv>")
}

gff_path <- args[1]
out_file <- args[2]
species <- "GCF_v1"

get_cpbd_go <- function(gene_id, species = "GCF_v1", sleep_sec = 0.2) {
  url <- paste0(
    "http://citrus.hzau.edu.cn/geneFunc/result.php?",
    "program=gene&species=", species,
    "&searchword=", gene_id
  )

  Sys.sleep(sleep_sec)

  page <- tryCatch(read_html(url), error = function(e) NULL)

  if (is.null(page)) {
    return(data.table(gene_id = gene_id, GO = NA_character_, status = "failed_read"))
  }

  tabs <- tryCatch(html_table(page, fill = TRUE), error = function(e) list())

  if (length(tabs) == 0) {
    return(data.table(gene_id = gene_id, GO = NA_character_, status = "no_table"))
  }

  dt <- as.data.table(tabs[[1]])

  if (!"GO" %in% names(dt)) {
    return(data.table(gene_id = gene_id, GO = NA_character_, status = "no_GO_column"))
  }

  go_values <- unique(na.omit(dt$GO))
  go_values <- go_values[go_values != "" & go_values != "-"]

  if (length(go_values) == 0) {
    return(data.table(gene_id = gene_id, GO = NA_character_, status = "no_GO"))
  }

  data.table(gene_id = gene_id, GO = go_values, status = "ok")
}

gff <- import(gff_path)
genes <- gff[gff$type == "gene"]

gene_ids <- as.character(mcols(genes)$ID)
gene_ids <- sub("\\.g\\.v1\\.0$", "", gene_ids)
gene_ids <- unique(gene_ids)

message("Total genes: ", length(gene_ids))

all_res <- list()

for (i in seq_along(gene_ids)) {
  gene <- gene_ids[i]
  message("[", i, "/", length(gene_ids), "] ", gene)

  all_res[[gene]] <- get_cpbd_go(gene, species = species)

  if (i %% 200 == 0) {
    tmp <- rbindlist(all_res, fill = TRUE)
    fwrite(tmp, sub("\\.tsv$", "_checkpoint.tsv", out_file), sep = "\t")
  }
}

go_raw <- rbindlist(all_res, fill = TRUE)
go_ok <- go_raw[status == "ok" & !is.na(GO)]

go_long <- go_ok[
  ,
  .(GO_ID = unlist(regmatches(GO, gregexpr("GO:[0-9]+", GO)))),
  by = gene_id
]

go_long <- unique(go_long[GO_ID != ""])

fwrite(go_raw, sub("\\.tsv$", "_raw.tsv", out_file), sep = "\t")
fwrite(go_long, out_file, sep = "\t")

message("Saved gene-to-GO table: ", out_file)
message("Genes with GO: ", uniqueN(go_long$gene_id))
message("Gene-GO pairs: ", nrow(go_long))

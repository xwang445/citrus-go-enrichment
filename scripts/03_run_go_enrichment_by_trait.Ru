#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(data.table)
  library(clusterProfiler)
  library(enrichplot)
  library(ggplot2)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 4) {
  stop(
    "Usage: Rscript 03_run_go_enrichment_by_trait.R ",
    "<candidate_gene_dir> <gene2go_tsv> <go_terms_tsv> <output_dir>"
  )
}

candidate_genes_dir <- args[1]
gene2go_path <- args[2]
go_terms_path <- args[3]
output_dir <- args[4]

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

gene2go <- fread(gene2go_path)
go_terms <- fread(go_terms_path)

TERM2GENE <- gene2go[, .(GO_ID, gene_id)]
TERM2NAME <- go_terms[, .(GO_ID, Description)]

gene_files <- list.files(
  candidate_genes_dir,
  pattern = "_candidate_genes\\.txt$",
  full.names = TRUE
)

if (length(gene_files) == 0) {
  stop("No candidate gene files found in: ", candidate_genes_dir)
}

all_results <- list()

for (f in gene_files) {
  phenotype <- sub("_candidate_genes\\.txt$", "", basename(f))
  phenotype_safe <- gsub("[^A-Za-z0-9._-]", "_", phenotype)

  message("Processing: ", phenotype)

  genes <- scan(f, what = character(), quiet = TRUE)
  genes <- sub("\\.g\\.v1\\.0$", "", genes)
  genes <- unique(genes)
  genes <- genes[genes != "" & !is.na(genes)]

  if (length(genes) < 3) {
    message("  Skipped: fewer than 3 candidate genes")
    next
  }

  genes_with_go <- intersect(genes, TERM2GENE$gene_id)

  if (length(genes_with_go) < 3) {
    message("  Skipped: fewer than 3 genes with GO annotation")
    next
  }

  ego <- tryCatch(
    enricher(
      gene = genes_with_go,
      TERM2GENE = TERM2GENE,
      TERM2NAME = TERM2NAME,
      pAdjustMethod = "BH",
      pvalueCutoff = 0.05,
      qvalueCutoff = 0.2
    ),
    error = function(e) {
      message("  Enrichment failed: ", conditionMessage(e))
      NULL
    }
  )

  if (is.null(ego)) next

  ego_df <- as.data.frame(ego)

  if (nrow(ego_df) == 0) {
    message("  No significant GO terms")
    next
  }

  ego_df$Phenotype <- phenotype
  ego_df$N_candidate_genes <- length(genes)
  ego_df$N_genes_with_GO <- length(genes_with_go)

  fwrite(
    ego_df,
    file.path(output_dir, paste0(phenotype_safe, "_GO_enrichment.tsv")),
    sep = "\t"
  )

  p <- dotplot(
    ego,
    showCategory = min(15, nrow(ego_df)),
    font.size = 14
  ) +
    ggtitle(phenotype) +
    theme(
      plot.title = element_text(size = 18, face = "bold", hjust = 0.5),
      axis.text = element_text(size = 12),
      axis.title = element_text(size = 14)
    )

  ggsave(
    filename = file.path(output_dir, paste0(phenotype_safe, "_GO_dotplot.png")),
    plot = p,
    width = 8,
    height = 6,
    dpi = 300
  )

  all_results[[phenotype]] <- ego_df
}

if (length(all_results) > 0) {
  combined_results <- rbindlist(all_results, fill = TRUE)

  fwrite(
    combined_results,
    file.path(output_dir, "All_phenotypes_GO_enrichment.tsv"),
    sep = "\t"
  )
}

message("Done. Output directory: ", output_dir)

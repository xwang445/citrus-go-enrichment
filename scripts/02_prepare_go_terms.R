#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(data.table)
  library(GO.db)
  library(AnnotationDbi)
  library(httr2)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("Usage: Rscript 02_prepare_go_terms.R <gene2go_tsv> <output_go_terms_tsv>")
}

gene2go_path <- args[1]
out_file <- args[2]

gene2go <- fread(gene2go_path)

TERM2GENE <- gene2go[, .(GO_ID, gene_id)]

go_info <- AnnotationDbi::select(
  GO.db,
  keys = unique(TERM2GENE$GO_ID),
  columns = c("TERM", "ONTOLOGY"),
  keytype = "GOID"
)

TERM2NAME <- as.data.table(go_info)[
  !is.na(TERM),
  .(
    GO_ID = GOID,
    Description = TERM,
    Ontology = ONTOLOGY
  )
]

missing_go <- setdiff(unique(TERM2GENE$GO_ID), TERM2NAME$GO_ID)

resolve_go_quickgo <- function(go_id) {
  url <- paste0(
    "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/",
    URLencode(go_id)
  )

  res <- tryCatch(
    request(url) |> req_perform(),
    error = function(e) NULL
  )

  if (is.null(res)) return(NULL)

  dat <- fromJSON(resp_body_string(res))

  if (length(dat$results) == 0) return(NULL)

  data.table(
    GO_ID = go_id,
    Current_GO_ID = dat$results$id,
    Description = dat$results$name,
    Ontology = dat$results$aspect
  )
}

if (length(missing_go) > 0) {
  message("Resolving ", length(missing_go), " missing GO IDs using QuickGO...")

  quickgo_terms <- rbindlist(
    lapply(missing_go, resolve_go_quickgo),
    fill = TRUE
  )

  quickgo_terms <- quickgo_terms[
    !is.na(Description),
    .(
      GO_ID,
      Description,
      Ontology
    )
  ]

  TERM2NAME <- rbindlist(
    list(TERM2NAME, quickgo_terms),
    fill = TRUE
  )

  TERM2NAME <- unique(TERM2NAME, by = "GO_ID")
}

fwrite(TERM2NAME, out_file, sep = "\t")

message("Saved GO term description table: ", out_file)
message("GO terms with descriptions: ", nrow(TERM2NAME))

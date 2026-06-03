# Citrus GO Enrichment Pipeline

GO enrichment pipeline for Citrus clementina candidate genes using CPBD annotations.

## Installation

Install required R packages:

```r
install.packages(c("data.table", "jsonlite", "httr2", "rvest"))

BiocManager::install(c(
  "clusterProfiler",
  "enrichplot",
  "GO.db",
  "AnnotationDbi",
  "rtracklayer"
))
```

## Repository Structure

```text
citrus-go-enrichment/
├── scripts/
│   ├── 01_download_cpbd_gene2go.R
│   ├── 02_prepare_go_terms.R
│   └── 03_run_go_enrichment_by_trait.R
├── data/
├── results/
└── README.md
```

## Workflow

### Step 1. Build gene-to-GO annotation table

```bash
Rscript scripts/01_download_cpbd_gene2go.R \
  data/Cclementina_182_v1.0.gene_exons.gff3 \
  data/Cclementina_CPBD_gene2GO.tsv
```

### Step 2. Resolve GO term descriptions

```bash
Rscript scripts/02_prepare_go_terms.R \
  data/Cclementina_CPBD_gene2GO.tsv \
  data/Cclementina_GO_terms.tsv
```

### Step 3. Run GO enrichment

```bash
Rscript scripts/03_run_go_enrichment_by_trait.R \
  data/candidate_genes_by_trait \
  data/Cclementina_CPBD_gene2GO.tsv \
  data/Cclementina_GO_terms.tsv \
  results/GO_enrichment_plots
```

## Output

The pipeline generates:

```text
results/
├── All_phenotypes_GO_enrichment.tsv
├── Cytidine_GO_dotplot.png
├── Gamma.Aminobutyric.acid_GO_dotplot.png
└── ...
```

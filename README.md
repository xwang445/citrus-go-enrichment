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

## SQL-Based GO Enrichment Pipeline

The [SQL implementation](SQL_GO_enrichment/README.md) adds SQLite for reproducible integration of candidate genes, genomic coordinates, SNP associations and GO annotations. The existing R pipeline remains unchanged.

A normalized database uses primary and foreign keys for genes, traits, gene–GO mappings, association evidence and enrichment results, with source hashes and original identifiers retained for auditing. Ten reusable SQL queries cover candidate retrieval, GO joins, shared genes, annotation coverage, genomic intervals and metadata checks. Python performs ETL and validation; R/clusterProfiler performs enrichment using the original statistical parameters and background.

To reproduce the analysis, configure the original input locations using `SQL_GO_enrichment/config.example.json`, then run:

```bash
python3 SQL_GO_enrichment/scripts/run_all.py
```

See the [setup and input requirements](SQL_GO_enrichment/README.md#reproduce-the-analysis) before running. Databases, raw inputs, private configuration and generated reports are excluded from Git; lightweight validation and benchmark summaries are included.

Validation reproduced all 61 significant results across 12 of 16 traits exactly against the current saved results, and all 881 tested results matched a fresh file-based control. See the [validation report](SQL_GO_enrichment/docs/reference/validation_report.md) for the older output folder’s description-only differences and historical-version limitations.

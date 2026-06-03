# Citrus GO Enrichment Pipeline

This repository contains R scripts for building a Citrus clementina gene-to-GO annotation table from CPBD and running GO enrichment for candidate gene lists.

## Workflow

1. Download gene-to-GO annotations from CPBD.
2. Fill GO term descriptions using GO.db and QuickGO.
3. Run GO enrichment for candidate genes grouped by phenotype.
4. Generate enrichment tables and dotplots.

## Requirements

R packages:

- data.table
- rtracklayer
- rvest
- clusterProfiler
- enrichplot
- ggplot2
- GO.db
- AnnotationDbi
- httr2
- jsonlite

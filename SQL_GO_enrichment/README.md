# SQL-based citrus GWAS candidate annotation and GO enrichment

A separate, executed SQLite implementation of the existing Citrus clementina workflow. The original R pipeline and its history are preserved. Private input datasets and the generated SQLite database are not included in Git. Inputs are read from local configuration; the workflow does not download annotation datasets.

The current saved enrichment results reproduce **exactly**: 61 significant trait–GO results across 12 of 16 traits. Four traits have no significant terms. The fresh file-based control also matches all 881 tested trait–GO results. An older output folder has eight GO-description differences, with identical statistics.

## Reproduce the analysis

Requirements: Python 3.10+ with pandas; R with DBI, RSQLite, data.table, clusterProfiler, jsonlite, digest and ggplot2. The reference analysis used its existing environment without installation or modification. For a new Python environment, use `python3 -m venv .venv` followed by `.venv/bin/python -m pip install -r SQL_GO_enrichment/requirements.txt` from the repository root. Use a separate R library if the listed packages are not already available; do not modify an existing analysis environment implicitly. Versions are in `results/python_environment.json` and `results/R_session_info.txt` (clusterProfiler 4.10.1; DOSE 3.28.2).

From the repository root:

```bash
cp SQL_GO_enrichment/config.example.json SQL_GO_enrichment/config.json
# Edit config.json to point at your existing inputs before continuing.
python3 SQL_GO_enrichment/scripts/run_all.py
```

`config.json` is ignored by Git. Paths are resolved relative to the configuration file, so both relative and absolute input locations work. Alternatively set `SQL_GO_CONFIG` to a configuration file outside the repository; Python and R use the same variable. The example `repository` value points to this repository. The reference snapshot has:

| Configuration field | Required content |
|---|---|
| `candidate_directory` | 16 headerless `*_candidate_genes.txt` files; saved `GO_enrichment_results/` TSVs and run summary; older `GO_enrichment_plots/` TSVs when available |
| `annotation_directory` | `Cclementina_182_v1.0.gene_exons.gff3`, `Cclementina_CPBD_gene2GO.tsv`, `Cclementina_CPBD_gene2GO_raw.tsv`, `Cclementina_GO_terms.tsv` |
| `association_file` | `significant_SNP_gene_annotation_50kb_forced_scaffold.tsv` with the 14 columns documented in the inventory |
| `original_script` | Original `02_run_go_enrichment_by_trait.R`, used as provenance; never executed in place |
| `repository` | Existing repository containing the original R scripts |

The full validation is intentionally tied to the inspected scientific snapshot. Without the original datasets, run the portable synthetic schema/query checks instead:

```bash
python3 -m unittest discover -s SQL_GO_enrichment/tests -p test_schema.py -v
```

The fixture uses clearly synthetic IDs and tests database behavior only; it is not biological evidence. Full reruns require the private/local input resources above. No replacement background or annotation relationships are generated.

For individual stages, first run `cd SQL_GO_enrichment`.

Individual stages:

```bash
python3 scripts/00_inspect_inputs.py
python3 scripts/01_build_database.py
python3 scripts/02_validate_database.py
Rscript scripts/03_run_sql_go_enrichment.R
python3 scripts/04_compare_results.py
Rscript scripts/05_benchmark.R
python3 -m unittest discover -s tests -v
python3 scripts/06_finalize_documentation.py
```

Each rerun refreshes only this project's generated reports, plots and the `sql_current` result rows. Database builds with identical source hashes are a no-op. The builder refuses to replace an existing database when source hashes differ. To test a fresh build without replacing the delivered database:

```bash
python3 scripts/01_build_database.py --database database/citrus_gwas_fresh.sqlite
python3 scripts/02_validate_database.py --database database/citrus_gwas_fresh.sqlite
```

For a different annotation snapshot, use a separate copy of this project and update `config.json`; inspect before building a fresh database. Snapshot-count tests deliberately require review when inputs change. No dependency installer is run automatically. The published example contains only relative paths; configure your own source locations before execution.

## Original and SQL workflows

The original R workflow strips the terminal `.g.v1.0` gene-ID suffix, joins candidate lists to the CPBD mapping, and calls `clusterProfiler::enricher`. GO.db/QuickGO descriptions come from the existing term snapshot. See the [reference repository](https://github.com/xwang445/citrus-go-enrichment); the local checked-out enrichment filename ends in `.Ru`, although its README says `.R`. The external `02_run_go_enrichment_by_trait.R` supplies the saved-results workflow.

```text
Original annotation files
          |
          v
     Python ETL
          |
          v
     SQLite Database
          |
     +----+----+
     |         |
     v         v
 SQL Queries   Metadata QC
     |
     v
 Candidate Gene Sets
     |
     v
 R clusterProfiler
     |
     v
 GO Enrichment Results
     |
     v
 Original vs SQL Validation
```

Python/pandas inventories and validates inputs; sqlite3 loads normalized relations in a transaction. SQL retrieves candidates, annotations and the background. R performs the statistical testing and creates dotplots. A file-based R control reads original files independently and runs with the original implicit universe.

## Data sources and architecture

Detailed paths, column names, row counts, missing values, duplicates and relationships are in `docs/reference/input_inventory.md`; the complete local manifest is generated as `docs/generated/input_manifest.json`. `docs/generated/recursive_file_inventory.csv` includes all files below the source candidate directory except Git internals and this generated project.

The database contains 15 application tables:

| Table | Imported/computed rows | Purpose |
|---|---:|---|
| sources | 54 | Paths, input row counts and SHA-256 provenance |
| genes | 24,533 | GFF3 gene coordinates and strand |
| gene_aliases | 70,835 | Original identifiers per source |
| traits | 16 | Original filename-based trait names |
| trait_genes | 3,120 | Unique candidate memberships; 2,423 distinct genes |
| candidate_records | 3,120 | Original candidate tokens and order |
| go_terms | 2,441 | Original/current GO IDs, descriptions, ontology and provider |
| gene_go | 38,855 | CPBD gene–GO pairs |
| annotation_records | 34,980 | Raw CPBD GO text and retrieval status |
| associations | 280 | Trait–SNP observations with P-values |
| association_genes | 3,499 | SNP-associated genes and distances |
| association_records | 3,499 | Complete source-row audit records |
| analysis_runs | 1 | Statistical parameters and runtime provenance |
| enrichment_results | 881 | All tested terms, 61 marked significant |
| enrichment_genes | 2,617 | Normalized result gene memberships |

`background_genes` is a view containing the 16,226 unique annotated genes. `sql/schema.sql`, `sql/indexes.sql` and `docs/reference/database_schema.md` describe keys, foreign keys, checks, provenance and indexes. SQLite may also create its internal statistics table.

All missing metabolite classes remain NULL. Original and forced SNP chromosome labels are both retained. Candidate membership comes only from the candidate files. No P-values, trait classes, evidence codes, GO ancestors or annotation relationships are inferred.

## ETL and integrity

The database is built in a temporary file and renamed only after successful import and validation. Parameterized statements protect data values; all connections enable foreign keys. The exact identifier transformation used by the original pipeline is retained; original strings and source hashes make it auditable.

Invalid records abort or produce explicit import issues; duplicates are detected and logged rather than silently ignored. This snapshot has zero import issues. The raw CPBD file retains 6 failed-read and 8,301 no-GO observations, rather than interpreting these as proven biological absence. Intermediate checkpoint files are inventoried, not merged into the final mapping. Non-gene GFF3 features remain available in the original reference file.

## Ten SQL query examples

The CLI binds values to SQL parameters and returns CSV. Each numbered query is a separate file in `sql/queries/`.

```bash
# 1. Candidates for a trait
python3 scripts/query.py 1 --trait Cytidine
# 2. Candidate GO annotations
python3 scripts/query.py 2 --trait Cytidine
# 3. Genes shared by traits
python3 scripts/query.py 3
# 4. GO terms represented in multiple traits
python3 scripts/query.py 4
# 5. Candidate counts per trait
python3 scripts/query.py 5
# 6. Annotation coverage per trait
python3 scripts/query.py 6
# 7. Candidates lacking a GO mapping
python3 scripts/query.py 7
# 8. GO terms ranked by distinct candidate genes
python3 scripts/query.py 8
# 9. Candidates overlapping a 1-based inclusive scaffold interval
python3 scripts/query.py 9 --chromosome scaffold_8 --start 24490000 --end 24510000
# 10. Missing metadata, duplicate relationships, foreign-key violations
python3 scripts/query.py 10
```

The validation stage executes all ten and saves example CSVs in `results/query_*.csv`. Queries demonstrate inner/left joins, CTEs, grouping, HAVING, DISTINCT counts, filtering and ordering. A NULL class is a reported metadata gap, not an integrity failure.

## Enrichment methodology

Preserved settings: hypergeometric testing through `clusterProfiler::enricher`, BH adjustment, p-value cutoff 0.05, q-value cutoff 0.2, gene-set sizes 10–500, and pooled GO categories without ancestor expansion. clusterProfiler handles its standard raw/adjusted P-value and q-value filtering. Both all-tested and filtered tables are saved; statistics are never recomputed in SQL.

The explicit SQL background equals the original default: all unique genes present in TERM2GENE, not all GFF genes. Gene and mapping file order is retained for deterministic result gene strings. Gene sets with fewer than three candidates or annotated genes are skipped. Historical package versions are unknown; current defaults and version information are recorded. Original/current GO-ID differences (15 terms) are retained without remapping. Source ontology labels preserve both abbreviations and QuickGO long names; no ontology-specific tests are introduced.

`results/enrichment/` contains per-trait TSVs, all-tested TSVs, combined significant results, run summary, parameters and 12 dotplots. The plots display gene counts and adjusted P-values; their layout is not intended to reproduce the original multi-panel figure.

## Validation results

- All 71 database checks and 7 integration tests passed for the original delivery. The portable package adds four synthetic schema/query tests; all 11 tests are included in a full run.
- Two independent fresh database builds match imported table contents; repeating either build leaves database bytes unchanged.
- Exact source candidate sets, GO pairs, term metadata, background and missing-annotation sets are verified.
- Current saved output: 626 exact comparisons, plus 48 exact summary comparisons.
- Fresh file control: 504 exact significant-output comparisons and 7,064 exact all-tested comparisons.
- Older plot output: 614 exact comparisons, eight description-only differences and four absent historical outputs. Missing files are not assumed to prove zero enrichment.
- All 54 inventoried source-file hashes remain unchanged.

The generated `results/validation_comparison.csv` aligns rows by trait and GO ID and distinguishes exact, approximate, differing and missing observations. Floating-point tolerance is relative 1e-10 / absolute 1e-14. The current results needed no tolerance: values matched exactly. `docs/reference/validation_report.md` explains the older label differences. Historical all-tested results were unavailable, so those are validated against the fresh control only.

## Performance

`results/sql_performance_benchmark.csv` measures six operations under four configurations, with equal-result checks, seven batches of 20 repetitions, and result-object memory sizes. `results/sql_query_plans.csv` records EXPLAIN QUERY PLAN. See `docs/reference/performance_report.md` for measured times.

In the initial measurements, SQLite was faster for the five requested operations; data.table was faster for the extra selective term lookup. Secondary indexes improved shared-gene and GO lookup operations but did not consistently improve full aggregations. These warm-cache, small-data measurements exclude ingestion and enrichment, and cannot establish a general or end-to-end speed advantage. Memory numbers describe returned objects, not peak process memory.

## Biological integration, metadata and FAIR principles

The relations integrate candidate genes, genomic coordinates, association evidence and functional annotations while retaining their distinct provenance. Explicit keys and constraints prevent orphan relationships; raw source records support auditing. Missing data and retrieval failures remain distinguishable from absent biological functions. Hashes, documented parameters, runnable scripts, version reports and tests make results reproducible.

Stable source identifiers, discoverable inventories and documented schemas support findability and interoperability. Reusable SQL and open TSV/SQLite formats support reuse. Accessibility is limited to the local source files and their original providers: this project does not claim to publish the source data, supply a data license, or fully satisfy FAIR through local storage alone.

## Published files and local outputs

The repository contains code, SQL, configuration examples, and reviewed documentation. `docs/reference/` and `results/reference/` contain lightweight reports from the validated reference snapshot, with local machine paths removed. They are not overwritten by reruns. Local reports are written to `docs/generated/` and `results/`, and the database is written to `database/`; these generated artifacts are ignored by Git. Full comparison tables, source manifests and session logs remain local because they may include filesystem paths or detailed gene-level data.

The source inventory in the published report uses basenames, not machine-specific locations. The unabridged paths and hashes remain in each local generated manifest. The benchmark summaries represent one measured run on one machine, not guaranteed performance on other hardware.

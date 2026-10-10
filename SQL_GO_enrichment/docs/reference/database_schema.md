# Database schema

SQLite foreign keys are enabled on every Python and R connection. Coordinates are 1-based inclusive. Gene identifiers remove only the documented terminal `.g.v1.0`; original strings are retained. All tables use primary keys; relationships use foreign keys. Missing metabolite class is NULL.

| Table | Rows | Columns (PK positions) |
|---|---:|---|
| sources | 54 | source_id INTEGER [PK1], path TEXT, sha256 TEXT, format TEXT, input_rows INTEGER |
| genes | 24533 | gene_id TEXT [PK1], chromosome TEXT, start_position INTEGER, end_position INTEGER, strand TEXT, annotation_source INTEGER |
| gene_aliases | 70835 | original_id TEXT [PK1], gene_id TEXT, source_id INTEGER [PK2] |
| traits | 16 | trait_id INTEGER [PK1], trait_name TEXT, metabolite_class TEXT |
| trait_genes | 3120 | trait_id INTEGER [PK1], gene_id TEXT [PK2] |
| candidate_records | 3120 | source_id INTEGER [PK1], row_number INTEGER [PK2], trait_id INTEGER, gene_id TEXT, original_id TEXT |
| go_terms | 2441 | go_id TEXT [PK1], go_name TEXT, ontology TEXT, current_go_id TEXT, annotation_provider TEXT, source_id INTEGER |
| gene_go | 38855 | gene_id TEXT [PK1], go_id TEXT [PK2], source_id INTEGER |
| annotation_records | 34980 | source_id INTEGER [PK1], row_number INTEGER [PK2], gene_id TEXT, raw_go TEXT, status TEXT |
| associations | 280 | association_id INTEGER [PK1], trait_id INTEGER, snp_id TEXT, chromosome_original TEXT, chromosome_forced TEXT, position INTEGER, p_value REAL, minus_log10_p REAL, source_id INTEGER |
| association_genes | 3499 | association_id INTEGER [PK1], gene_id TEXT [PK2], distance_to_gene INTEGER, annotation TEXT, gene_name TEXT, reported_chromosome TEXT, reported_start INTEGER, reported_end INTEGER, original_gene_id TEXT |
| association_records | 3499 | source_id INTEGER [PK1], row_number INTEGER [PK2], association_id INTEGER, gene_id TEXT, raw_json TEXT |
| analysis_runs | 1 | run_id TEXT [PK1], parameters_json TEXT, session_info TEXT, input_manifest_sha256 TEXT |
| enrichment_results | 881 | run_id TEXT [PK1], trait_id INTEGER [PK2], go_id TEXT [PK3], p_value REAL, adjusted_p_value REAL, q_value REAL, gene_count INTEGER, background_count INTEGER, gene_ratio TEXT, background_ratio TEXT, significant INTEGER |
| enrichment_genes | 2617 | run_id TEXT [PK1], trait_id INTEGER [PK2], go_id TEXT [PK3], gene_id TEXT [PK4] |

## Relationships and provenance

sources stores the input path, SHA-256 hash, format and inspected row count, including reference-only comparison outputs. genes links to its GFF source. gene_aliases retains original IDs per source. traits and genes are linked by trait_genes; candidate_records preserves every source token, row order and membership provenance. gene_go links genes and go_terms with its CPBD mapping source. annotation_records preserves every raw CPBD observation and retrieval status.

associations stores one trait–SNP observation per source, including original/forced chromosome and P-value. association_genes links observations to genes, preserves reported coordinates/distance/labels, and is checked against GFF coordinates during ETL. association_records preserves every original row as JSON. It is an explicit audit layer; scientific retrieval uses normalized tables. No associations create candidate membership.

analysis_runs holds parameters, package session information and manifest hash once per run. enrichment_results contains all tested terms, with significant flag and raw/adjusted P-values, q-values, counts and ratios. enrichment_genes normalizes result gene membership. Ontology and term names are retrieved from go_terms instead of copied into result rows. background_genes is a view of DISTINCT gene_go genes (16,226), not a fabricated genome-wide universe.

GO ontology values retain source spelling: BP/CC/MF and QuickGO biological_process/cellular_component/molecular_function. These correspond to three categories but are pooled in the original statistical analysis. Fifteen Current_GO_ID values differ from GO_ID; they remain metadata and are not substituted. There are six failed_read raw CPBD observations and 8,301 no_GO observations; all are preserved.

## Indexes and constraints

Composite primary keys enforce unique trait–gene and gene–GO relationships. Secondary indexes support reverse GO lookup, reverse trait membership, scaffold interval queries and association gene retrieval. Coordinate and P-value CHECK constraints reject invalid values; ETL validates source relationships and fails on inconsistent SNP metadata. SQL parameter values are bound rather than interpolated. indexes.sql contains all named secondary indexes.

## Build behavior

A new database is built in a temporary file, using a transaction for all imports, checked, indexed and atomically renamed. Identical source hashes make a repeated build a no-op. Changed inputs require a new --database target: an existing database is never replaced by the builder. Duplicate candidate and mapping relationships are logged; every candidate source row remains in candidate_records. Missing GO descriptions create explicit NULL metadata and a logged issue. Conflicting gene coordinates or SNP observations abort rather than silently choose a record.

The inspected snapshot has no duplicate pairs, invalid coordinates, missing gene coordinates, missing GO metadata or referential-integrity violations. import_counts.json reports the import-only stage; final_database_counts.json includes computed enrichment.

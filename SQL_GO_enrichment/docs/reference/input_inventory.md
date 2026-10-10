# Input inventory

Inspection completed before schema implementation. All source files are read-only inputs. This published inventory replaces absolute source paths with basenames. Full per-column missing counts, duplicate counts, SHA-256 and feature counts are generated locally in `docs/generated/input_manifest.json`. Repeated gene/GO identifiers in mappings are expected many-to-many relationships, not duplicate pairs.

| Path | Rows | Columns | Duplicate rows | Missing values |
|---|---:|---|---:|---|
| 02_run_go_enrichment_by_trait.R | 289 | text | n/a | "n/a" |
| Cclementina_182_v1.0.gene_exons.gff3 | 506439 | seqid, source, type, start, end, score, strand, phase, attributes | 0 | 0 |
| Cclementina_CPBD_gene2GO.tsv | 38855 | gene_id, GO_ID | 0 | {"gene_id": 0, "GO_ID": 0} |
| Cclementina_CPBD_gene2GO_checkpoint.tsv | 34807 | gene_id, GO, status | 0 | {"gene_id": 0, "GO": 8253, "status": 0} |
| Cclementina_CPBD_gene2GO_raw.tsv | 34980 | gene_id, GO, status | 0 | {"gene_id": 0, "GO": 8307, "status": 0} |
| Cclementina_GO_terms.tsv | 2441 | GO_ID, Current_GO_ID, Description, Ontology, Source | 0 | {"GO_ID": 0, "Current_GO_ID": 0, "Description": 0, "Ontology": 0, "Source": 0} |
| Candidate_gene_GO_annotation_counts_by_trait.tsv | 16 | Trait, N_total_candidate_genes, N_candidate_genes_with_GO, Percent_with_GO | 0 | {"Trait": 0, "N_total_candidate_genes": 0, "N_candidate_genes_with_GO": 0, "Percent_with_GO": 0} |
| Candidate_gene_counts_by_trait.tsv | 16 | Trait, N_candidate_genes | 0 | {"Trait": 0, "N_candidate_genes": 0} |
| Cytidine_candidate_genes.txt | 13 | gene_id (headerless) | 0 | 0 |
| All_phenotypes_GO_enrichment.tsv | 61 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Cytidine_GO_enrichment.tsv | 4 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Gamma.Aminobutyric.acid_GO_enrichment.tsv | 2 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Guanosine_GO_enrichment.tsv | 1 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Lysine_GO_enrichment.tsv | 6 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Methionine.sulfoxide_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| NAD_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Phenylalanine_GO_enrichment.tsv | 12 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Threonine_GO_enrichment.tsv | 5 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Tyrosine_GO_enrichment.tsv | 12 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_62_GO_enrichment.tsv | 4 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_696_GO_enrichment.tsv | 6 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_98_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Cytidine_GO_enrichment.tsv | 4 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| GO_enrichment_run_summary.tsv | 16 | Phenotype, N_candidate_genes, N_genes_with_GO, Status | 0 | {"Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0, "Status": 0} |
| Gamma.Aminobutyric.acid_GO_enrichment.tsv | 2 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Guanosine_GO_enrichment.tsv | 1 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Lysine_GO_enrichment.tsv | 6 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Methionine.sulfoxide_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| NAD_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Phenylalanine_GO_enrichment.tsv | 12 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Threonine_GO_enrichment.tsv | 5 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Tyrosine_GO_enrichment.tsv | 12 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_62_GO_enrichment.tsv | 4 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_696_GO_enrichment.tsv | 6 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| mole_98_GO_enrichment.tsv | 3 | ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count, Phenotype, N_candidate_genes, N_genes_with_GO | 0 | {"ID": 0, "Description": 0, "GeneRatio": 0, "BgRatio": 0, "pvalue": 0, "p.adjust": 0, "qvalue": 0, "geneID": 0, "Count": 0, "Phenotype": 0, "N_candidate_genes": 0, "N_genes_with_GO": 0} |
| Gamma.Aminobutyric.acid_candidate_genes.txt | 195 | gene_id (headerless) | 0 | 0 |
| Guanosine_candidate_genes.txt | 17 | gene_id (headerless) | 0 | 0 |
| Isoleucine_candidate_genes.txt | 29 | gene_id (headerless) | 0 | 0 |
| Leucine_candidate_genes.txt | 33 | gene_id (headerless) | 0 | 0 |
| Lysine_candidate_genes.txt | 11 | gene_id (headerless) | 0 | 0 |
| Methionine.sulfoxide_candidate_genes.txt | 37 | gene_id (headerless) | 0 | 0 |
| NAD_candidate_genes.txt | 279 | gene_id (headerless) | 0 | 0 |
| Phenylalanine_candidate_genes.txt | 31 | gene_id (headerless) | 0 | 0 |
| Threonine_candidate_genes.txt | 15 | gene_id (headerless) | 0 | 0 |
| Tyrosine_candidate_genes.txt | 31 | gene_id (headerless) | 0 | 0 |
| UDP.glucose_candidate_genes.txt | 59 | gene_id (headerless) | 0 | 0 |
| 01_download_cpbd_gene2go.R | 95 | text | n/a | "n/a" |
| 02_prepare_go_terms.R | 95 | text | n/a | "n/a" |
| 03_run_go_enrichment_by_trait.Ru | 134 | text | n/a | "n/a" |
| mole_228_candidate_genes.txt | 13 | gene_id (headerless) | 0 | 0 |
| mole_62_candidate_genes.txt | 72 | gene_id (headerless) | 0 | 0 |
| mole_696_candidate_genes.txt | 2196 | gene_id (headerless) | 0 | 0 |
| mole_98_candidate_genes.txt | 89 | gene_id (headerless) | 0 | 0 |
| significant_SNP_gene_annotation_50kb_forced_scaffold.tsv | 3499 | Trait, SNP, SNP_chr_original, SNP_chr_forced, SNP_position_original, P_value, MinusLog10P, gene_id, gene_name, gene_chr, gene_start, gene_end, distance_to_gene, annotation | 0 | {"Trait": 0, "SNP": 0, "SNP_chr_original": 0, "SNP_chr_forced": 0, "SNP_position_original": 0, "P_value": 0, "MinusLog10P": 0, "gene_id": 0, "gene_name": 0, "gene_chr": 0, "gene_start": 0, "gene_end": 0, "distance_to_gene": 0, "annotation": 0} |

## Relationships and scientific parameters

Sixteen headerless candidate lists define trait membership. Trait names are filename stems, including literal dots and unidentified `mole_*` names. No supported metabolite-class mapping was found. Only the terminal `.g.v1.0` suffix is removed, exactly as in the original R script; original identifiers are retained in alias and source-row tables. GFF3 gene features provide 1-based inclusive scaffold coordinates and strand. Exon/CDS/transcript features are not separate genes.

CPBD mapping contains gene_id/GO_ID pairs. The raw CPBD file retains retrieval status and original GO text, including failed/unannotated records. The checkpoint is an intermediate snapshot, inventoried but not combined with the final mapping. GO descriptions retain GO_ID, Current_GO_ID, Description, Ontology and Source (GO.db/QuickGO); current IDs do not replace original IDs. No GO ancestor expansion is performed.

The external 02_run_go_enrichment_by_trait.R matches the saved GO_enrichment_results convention. The checked-out repository has a `.Ru` enrichment script despite its README advertising `.R`. GitHub was accessible: https://github.com/xwang445/citrus-go-enrichment . The older GO_enrichment_plots output is retained as a separate comparison cohort.

Original enrichment uses clusterProfiler::enricher with BH, pvalueCutoff=0.05, qvalueCutoff=0.2, no explicit universe, and no ontology split. Thus background is unique genes in TERM2GENE, not all GFF genes. Installed defaults minGSSize=10 and maxGSSize=500 are recorded explicitly for reproduction. Fewer than three candidate or annotated genes are skipped. The historical package versions were not recorded; current R session/package versions will be captured.

The 3,499-row significant_SNP_gene_annotation_50kb_forced_scaffold.tsv supplies explicit trait–SNP–gene relationships and P-values, including original and forced scaffold labels. These fields are preserved without independently validating the forced chromosome conversion. Candidate lists remain authoritative. `signi_snps_annotation.tsv` is a headerless genotype matrix, not a gene annotation table. Nearby `finalgenes.tsv` and `9114_GO.tsv` are headerless legacy subsets with no justified trait linkage; `metabolites_with_candidate_genes.csv` contains 31 older CDS-level records. They do not replace the identified pipeline inputs.

## Implementation plan

1. Normalize gene, trait, term and many-to-many tables; retain source hashes and raw records.
2. Build transactionally, log inconsistencies, verify counts and foreign keys, execute ten parameterized queries.
3. Retrieve exact R inputs from SQL, run clusterProfiler and compare both saved cohorts plus a fresh file-based control.
4. Measure equivalent SQLite/data.table operations, verify equal outputs, inspect indexed/unindexed plans.
5. Test repeatability and constraints; document results, rerun commands and limitations.

A complete recursive file listing (including plots, PDF and miscellaneous files) is in `docs/generated/recursive_file_inventory.csv`; row counts are not applicable to images and PDFs.

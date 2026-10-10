# Performance report

All 24 engine/operation outputs matched the independently calculated data.table result after sorting. Times are warm-cache medians, in milliseconds, for 7 batches of 20 repetitions. Loading inputs and constructing databases are excluded.

| Operation | SQLite on disk | R data.table | RAM SQLite indexed | RAM without secondary indexes |
|---|---:|---:|---:|---:|
| annotation_coverage | 0.850 | 2.500 | 0.850 | 0.850 |
| candidate_retrieval | 0.100 | 0.350 | 0.100 | 0.100 |
| gene_to_go_join | 2.450 | 6.850 | 2.450 | 2.450 |
| multi_trait_aggregation | 2.850 | 16.650 | 2.800 | 2.800 |
| shared_genes | 0.450 | 11.100 | 0.450 | 0.800 |
| term_lookup | 0.550 | 0.400 | 0.500 | 1.450 |

These measurements describe this small dataset and these implementations, not a general SQLite advantage. The original workflow provides candidate/annotation retrieval operations; coverage, shared-gene and aggregation comparisons use equivalent data.table implementations rather than claiming a historical benchmark. data.table may create automatic indexes during warm-up. At this scale timer quantization and binding overhead matter.

The controlled index comparison uses two in-memory copies, retaining primary-key indexes in both. Examine `results/sql_query_plans.csv` alongside timings: reverse gene membership and selective term lookup benefit from secondary indexes, whereas primary-key lookups already have indexes and some aggregation workloads gain little. Returned object sizes are measured; these are not peak process memory. All build and file-loading costs are excluded. No claim is made about end-to-end enrichment speed.

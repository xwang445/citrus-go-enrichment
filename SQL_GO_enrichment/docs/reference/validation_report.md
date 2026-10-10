# Validation report

Database validation passed all 71 checks. Full checks: `results/database_validation.csv`. Source-vs-SQL candidate and mapping sets are compared exactly, including missing-annotation detection. Statistical comparisons join by trait and original GO ID; duplicate keys fail. Gene membership compares unordered sets. Floats use relative tolerance 1e-10 and absolute tolerance 1e-14; exact equality is reported separately.

```
cohort                         status
GO_enrichment_plots            different              8
                               exact                614
                               missing_original       4
GO_enrichment_results          exact                626
fresh_file_control             exact                504
fresh_file_control_all_tested  exact               7064
input_counts                   exact                  5
original_summary               exact                 48
```

Discrepant comparisons: 8. Missing historical observations: 4. The two saved output directories are evaluated separately; absence in the old plot directory is not treated as evidence of a zero-result analysis. For GO_enrichment_results, the saved summary establishes zero significant terms.

A fresh file-based R control independently reads candidate and annotation files, keeps the original implicit universe, and tests all terms in the same current R environment. SQL uses an explicit universe retrieved from gene_go. Both significant and all-tested results are compared. This establishes retrieval equivalence without attributing differences to SQL. Saved historical tables validate significant terms only; historical nonsignificant P-values and package versions were not saved.

All available historical statistical values, ratios, counts and gene memberships reproduce exactly. The current GO_enrichment_results cohort also matches descriptions exactly. No scientific parameters were altered to obtain agreement.

The older GO_enrichment_plots cohort has eight description-only differences across four GO IDs: the saved descriptions are literal GO IDs, whereas the available term table supplies names (including obsolete-term labels). All corresponding P-values, adjusted P-values, q-values, ratios and genes match exactly. These are annotation-label differences, not altered enrichment statistics. Full differences:

```
             cohort         trait      go_id      metric   original                                                     sql    status
GO_enrichment_plots        Lysine GO:0005887 Description GO:0005887                                         plasma membrane different
GO_enrichment_plots        Lysine GO:0016307 Description GO:0016307 obsolete phosphatidylinositol phosphate kinase activity different
GO_enrichment_plots Phenylalanine GO:0005887 Description GO:0005887                                         plasma membrane different
GO_enrichment_plots Phenylalanine GO:0016307 Description GO:0016307 obsolete phosphatidylinositol phosphate kinase activity different
GO_enrichment_plots      Tyrosine GO:0005887 Description GO:0005887                                         plasma membrane different
GO_enrichment_plots      Tyrosine GO:0016307 Description GO:0016307 obsolete phosphatidylinositol phosphate kinase activity different
GO_enrichment_plots      mole_696 GO:0006073 Description GO:0006073              obsolete cellular glucan metabolic process different
GO_enrichment_plots      mole_696 GO:0097573 Description GO:0097573            obsolete glutathione oxidoreductase activity different
```

## Scope and limitations

The historical background is recovered from the original implicit-universe code and checked against saved BgRatio denominators. No background, evidence codes, metabolite classes or GO ancestor relationships are invented. The annotation snapshot is reused offline. Source provenance is not an experimental GO evidence code. Original scaffold forcing is recorded, not independently justified. Current_GO_ID is retained as metadata; remapping would change the original analysis.

The full GFF3 is inventoried; gene rows supply the gene entity. Non-gene features remain in the unchanged source, not duplicated as genes. Intermediate checkpoint data is not merged into the final annotation snapshot. Original results remain external comparison sources rather than being relabeled as newly computed results.

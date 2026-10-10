CREATE INDEX idx_gene_go_term ON gene_go(go_id,gene_id);
CREATE INDEX idx_trait_genes_gene ON trait_genes(gene_id,trait_id);
CREATE INDEX idx_genes_interval ON genes(chromosome,start_position,end_position);
CREATE INDEX idx_association_genes_gene ON association_genes(gene_id);
CREATE INDEX idx_candidates_gene ON candidate_records(gene_id,trait_id);

SELECT t.trait_name,g.* FROM traits t INNER JOIN trait_genes tg USING(trait_id) INNER JOIN genes g USING(gene_id) WHERE t.trait_name=:trait ORDER BY g.gene_id;

SELECT t.trait_name,tg.gene_id FROM traits t INNER JOIN trait_genes tg USING(trait_id) LEFT JOIN gene_go gg USING(gene_id) WHERE gg.go_id IS NULL ORDER BY t.trait_name,tg.gene_id;

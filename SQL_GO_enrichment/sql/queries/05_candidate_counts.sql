SELECT t.trait_name,COUNT(tg.gene_id) AS candidate_count FROM traits t LEFT JOIN trait_genes tg USING(trait_id) GROUP BY t.trait_id ORDER BY t.trait_name;

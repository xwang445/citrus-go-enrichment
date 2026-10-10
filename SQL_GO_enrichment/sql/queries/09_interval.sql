SELECT DISTINCT g.* FROM genes g INNER JOIN trait_genes tg USING(gene_id) WHERE g.chromosome=:chromosome AND g.start_position<=:end AND g.end_position>=:start ORDER BY g.start_position,g.gene_id;

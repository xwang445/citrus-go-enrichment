SELECT gene_id,COUNT(DISTINCT trait_id) AS trait_count FROM trait_genes GROUP BY gene_id HAVING COUNT(DISTINCT trait_id)>1 ORDER BY trait_count DESC,gene_id;

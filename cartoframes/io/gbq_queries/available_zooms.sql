SELECT array_agg(z) AS available_zooms
    FROM (
        SELECT DISTINCT (z)
            FROM `{output_table}`
            ORDER BY z ASC
    ) q;

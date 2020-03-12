SELECT z AS zoom, (COUNTIF(mvt = FROM_BASE64('{oom_base64}')) / COUNT(*)) AS oom_ratio
    FROM  `{output_table}`
    GROUP by z
    ORDER by z;

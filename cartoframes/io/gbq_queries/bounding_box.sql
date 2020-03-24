SELECT MIN(xmin) AS xmin, MIN(ymin) AS ymin, MAX(xmax) AS xmax, MAX(ymax) AS ymax
    FROM `{prepare_table}`;

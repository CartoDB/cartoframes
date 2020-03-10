SELECT MIN(__xmin) AS xmin, MIN(__ymin) AS ymin, MAX(__xmax) AS xmax, MAX(__ymax) AS ymax
    FROM `{prepare_table}`;

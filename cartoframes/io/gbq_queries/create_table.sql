CREATE OR REPLACE TABLE `{output_table}`
    (
        z INT64 NOT NULL,
        x INT64 NOT NULL,
        y INT64 NOT NULL,
        mvt BYTES NOT NULL,
        quadkey INT64
    )
    -- The upper limit of the partition should be `{max_decimal_quadkey} + 1`, but as it is right now, we can use the extra `__UNPARTITIONED__` partition
    -- Also probably, the low zoom tiles (1, 2, ...) will go to the `__UNPARTITIONED__` partition, not a problem
    -- For the `0, 0, 0` `z, x, y` the `quadkey` is `NULL`, so it goes to the `__NULL__` partition
    PARTITION BY RANGE_BUCKET(quadkey, GENERATE_ARRAY({min_decimal_quadkey}, {max_decimal_quadkey}, {step_decimal_queadkey}))
    CLUSTER BY z, x, y;

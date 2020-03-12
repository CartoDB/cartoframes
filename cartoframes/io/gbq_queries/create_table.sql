CREATE OR REPLACE TABLE `{output_table}`
    (
        z INT64 NOT NULL,
        x INT64 NOT NULL,
        y INT64 NOT NULL,
        mvt BYTES NOT NULL,
        parent_quadkey INT64
    )
    -- The upper limit of the partition should be `{max_integer_quadkey} + 1`, but as it is right now, we can use the extra `__UNPARTITIONED__` partition
    -- Also probably, the low zoom tiles (1, 2, ...) will go to the `__UNPARTITIONED__` partition, not a problem
    -- For the `0, 0, 0` `z, x, y` the `parent_quadkey` is `NULL`, so it goes to the `__NULL__` partition
    PARTITION BY RANGE_BUCKET(parent_quadkey, GENERATE_ARRAY({min_integer_quadkey}, {max_integer_quadkey}, {step_integer_queadkey}))
    CLUSTER BY z, x, y;

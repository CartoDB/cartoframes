CREATE OR REPLACE TABLE `{prepare_table}`
    PARTITION BY RANGE_BUCKET(__partition, GENERATE_ARRAY(0, {prepare_partitions} - 1, 1))
    AS
    SELECT *, CAST(FLOOR({prepare_partitions} * RAND()) AS INT64) __partition  -- RAND() returns a FLOAT64 in the [0, 1) range
        FROM (
            -- Enforce geom and geoid columns exist
            WITH source_table AS (
                SELECT * EXCEPT ({geom_col}, {index_col}),
                        {geom_col} AS geom,
                        {index_col} AS geoid
                    FROM ({source_query}) q
            ),
            -- Prepare the auxiliar values
            geom_data AS (
                SELECT  geoid,
                        carto_tiler.ST_PrepareMVT(TO_HEX(ST_ASBinary(geom)), {tile_extent}) AS __prepared_struct
                    FROM source_table
            ),
            -- Prepare the json data using the data columns
            json_data AS (
                SELECT geoid, TO_JSON_STRING(subdata) data
                    FROM (
                        SELECT * EXCEPT (geom)
                            FROM source_table
                    ) subdata
            )
            -- Merge auxiliar values with the data
            SELECT  __prepared_struct.xmin AS xmin,
                    __prepared_struct.ymin AS ymin,
                    __prepared_struct.xmax AS xmax,
                    __prepared_struct.ymax AS ymax,
                    __prepared_struct.visible_zoom AS visible_zoom,
                    __prepared_struct.geom_3857 as geom,
                    b.data
                FROM geom_data a JOIN json_data b ON (a.geoid = b.geoid)

        ) _table;

CREATE OR REPLACE TABLE `{prepare_table}`
    PARTITION BY RANGE_BUCKET(__partition, GENERATE_ARRAY(0, {prepare_partitions} - 1, 1))
    AS
    SELECT *, CAST(FLOOR({prepare_partitions} * RAND()) AS INT64) __partition -- RAND() returns a FLOAT64 in the range of [0, 1)
      FROM (
        WITH source_table AS (
            SELECT * EXCEPT ({geom_col}, {index_col}),
                    {geom_col} AS geom,
                    {index_col} AS geoid
                FROM ({source_query}) q
        ),
        json_data AS (
            SELECT geoid, TO_JSON_STRING(d) data FROM (
                SELECT * EXCEPT (geom) FROM source_table
            ) d
        ),
        geom_data AS (
            SELECT a.geoid AS __geoid,
                    CONCAT('{{"type": "Feature", "properties": ', b.data,  -- double {{ because of Python's format
                           ', "geometry": ', ST_AsGeoJSON(geom), '}}') AS __geojson,  -- double }} because of Python's format
                    carto_tiler.ST_PrepareMVT(TO_HEX(ST_ASBinary(geom)), 4096) AS prepared_struct
                FROM source_table a JOIN json_data b ON (a.geoid = b.geoid)
        )
        SELECT * EXCEPT (prepared_struct),
                prepared_struct.xmin AS __xmin,
                prepared_struct.ymin AS __ymin,
                prepared_struct.xmax AS __xmax,
                prepared_struct.ymax AS __ymax,
                prepared_struct.visible_zoom AS __visible_zoom,
                prepared_struct.geom_3857 AS __geom
            FROM geom_data
      ) _table;

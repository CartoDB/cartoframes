INSERT INTO `{output_table}` (z, x, y, mvt, quadkey)
    WITH tile_bbox AS (
        SELECT carto_tiler.ST_TileEnvelope_bbox({xmin}, {ymin}, {xmax}, {ymax}, z) AS tiles
            FROM UNNEST({wasm_zooms}) z
    ),
    tile_list AS (
        SELECT tiles.z AS z, x, y
            FROM tile_bbox,
                UNNEST(GENERATE_ARRAY(tiles.xmin, tiles.xmax, 1)) AS x,
                UNNEST(GENERATE_ARRAY(tiles.ymin, tiles.ymax, 1)) AS y
    ),
    tiles AS (
        SELECT t.z AS __z, t.x AS __x, t.y AS __y,
                t.xmin AS __xmin, t.ymin AS __ymin, t.xmax AS __xmax, t.ymax AS __ymax
            FROM (
                SELECT carto_tiler.ST_TileEnvelope(z, x, y, 1 / {tile_buffer}) AS t
                    FROM tile_list
            ) _a
    ),
    tiles_with_data AS (
        SELECT __z AS z, __x AS x, __y AS y,
                CONCAT(SUBSTR(properties, 0, LENGTH(properties) - 1), ',"geom":"', geom, '"}}') AS data  -- double }} because of Python's format
            FROM (
                SELECT * EXCEPT (__geom, __xmin, __xmax, __ymin, __ymax, __visible_zoom, __geojson, __partition, __geoid),
                    JSON_EXTRACT(__geojson, "$.properties") AS properties,
                    carto_tiler.ST_AsMVTGeom(a.__geom, b.__z, b.__x, b.__y, {tile_extent}, 2) AS geom
                FROM tiles b
                    JOIN `{prepare_table}` a
                        ON (a.__visible_zoom <= (b.__z - LOG(4096 / 512, 2))
                            AND NOT ((a.__xmin > b.__xmax) OR (a.__xmax < b.__xmin) OR (a.__ymax < b.__ymin) OR (a.__ymin > b.__ymax)))
            ) __subquery
            WHERE geom IS NOT NULL
    )
    SELECT z, x, y, carto_tiler.ST_AsMVT(ARRAY_AGG(data), {tile_extent}, '') AS mvt,
            CAST(carto_tiler.ST_TileToQuadkeyDecimal(z, x, y, {quadkey_zoom}) AS INT64) AS quadkey
        FROM tiles_with_data
        GROUP BY z, x, y;

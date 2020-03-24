INSERT INTO `{output_table}` (z, x, y, mvt, parent_quadkey)
    WITH tile_bbox AS (
        SELECT carto_tiler.ST_TileEnvelope_bbox({xmin}, {ymin}, {xmax}, {ymax}, z) AS tiles
            FROM UNNEST({zooms}) z
    ),
    tile_list AS (
        SELECT tiles.z AS z, x, y
            FROM tile_bbox,
                UNNEST(GENERATE_ARRAY(tiles.xmin, tiles.xmax, 1)) AS x,
                UNNEST(GENERATE_ARRAY(tiles.ymin, tiles.ymax, 1)) AS y
    ),
    tiles AS (
        SELECT t.*
            FROM (
                SELECT carto_tiler.ST_TileEnvelope(z, x, y, 1 / {tile_buffer}) AS t
                    FROM tile_list
            ) _a
    ),
    tiles_with_data AS (
        SELECT z, x, y,
                CONCAT(RTRIM(data, '}}'), ',"geom":"', geom, '"}}') AS data  -- double }} because of Python's format
            FROM (
                SELECT a.data,
                        b.*,
                        a.geom AS geom
                    FROM tiles b
                        JOIN `{prepare_table}` a
                        ON ((a.visible_zoom <= b.z)
                            AND NOT ((a.xmin > b.xmax) OR (a.xmax < b.xmin) OR (a.ymax < b.ymin) OR (a.ymin > b.ymax)))
            ) __subquery
    ),
    joined_data AS (
        SELECT  z, x, y,
                CAST(carto_tiler.ST_TileToParentIntegerQuadkey(z, x, y, {quadkey_zoom}) AS INT64) AS parent_quadkey,
                ARRAY_AGG(data) AS data,
                ABS(MOD(z + x + y, 10)) AS query_partition
            FROM tiles_with_data
            GROUP BY z, x, y
    )
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 0
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 1
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 2
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 3
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 4
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 5
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 6
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 7
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 8
    UNION ALL
    SELECT z, x, y, carto_tiler.ST_AsMVT(data, {tile_extent}, FORMAT('{options}', z, x, y)) AS mvt, parent_quadkey FROM joined_data WHERE query_partition = 9;

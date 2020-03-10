INSERT INTO `{output_table}` (z, x, y, mvt, quadkey)
    WITH tile_bbox AS (
        SELECT carto_tiler.ST_TileEnvelope_bbox({xmin}, {ymin}, {xmax}, {ymax}, z) AS tiles
            FROM UNNEST({geojson_vt_base_zooms}) z
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
    inter AS (
        SELECT b.__z AS z, b.__x AS x, b.__y AS y, a.__geoid AS geoid
            FROM `{prepare_table}` a, tiles b
            WHERE (a.__visible_zoom <= (b.__z - LOG(4096 / {tile_extent}, 2))
                AND NOT ((a.__xmin > b.__xmax) OR (a.__xmax < b.__xmin) OR (a.__ymax < b.__ymin) OR (a.__ymin > b.__ymax)))
    ),
    nested_tiles AS (
        SELECT carto_tiler.ST_AsMVT_Single(b.z, b.x, b.y, array_agg(a.__geojson), {geojson_vt_zooms}, {tile_extent}) AS tile
            FROM inter b, `{prepare_table}` a
            WHERE a.__geoid = b.geoid
            GROUP BY z, x, y
    )
    SELECT flattened.z AS z, flattened.x AS x, flattened.y AS y, flattened.mvt AS mvt,
            CAST(carto_tiler.ST_TileToQuadkeyDecimal(flattened.z, flattened.x, flattened.y, {quadkey_zoom}) AS INT64) AS quadkey
        FROM nested_tiles
            CROSS JOIN UNNEST(nested_tiles.tile) flattened;

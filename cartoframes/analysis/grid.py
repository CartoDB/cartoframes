from tiletanic.tileschemes import WebMercator
from tiletanic.tilecover import cover_geometry
from shapely.geometry import box
import geopandas as gpd
import pandas as pd
from cartoframes import CartoDataFrame


class QuadGrid():

    def polyfill(self, input_gdf, zoom_level):
        tiler = WebMercator()
        # Transform input to 3857
        gdf = input_gdf.copy()
        if not gdf.crs:
            # assuming 4326 if not specified
            gdf.crs = 'epsg:4326'
        gdf = gdf.to_crs('epsg:3857')

        dfs = []

        for _, row in gdf.iterrows():
            tiles = cover_geometry(tiler, row['geometry'], zoom_level)
            resp = []
            for t in tiles:
                r = row.copy()
                r['geometry'] = box(*tiler.bbox(t))
                r['quadkey'] = tiler.quadkey(t)
                resp.append(r)

            dfs.append(pd.DataFrame(resp))

        r_gdf = CartoDataFrame(pd.concat(dfs).reset_index(drop=True))
        r_gdf.crs = 'epsg:3857'
        # Transforme to 4326
        r_gdf = r_gdf.to_crs('epsg:4326')

        # TODO: Fix it at CartoDataFrame class needs to reconvert to don't lose subclass.
        r_gdf = CartoDataFrame(r_gdf)
        r_gdf.crs = 'epsg:4326'
        return r_gdf

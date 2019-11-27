import mercantile
from shapely.geometry import box
import pandas as pd
from cartoframes import CartoDataFrame


class QuadGrid():

    def polyfill(self, input_gdf, zoom_level):

        dfs = []

        for _, row in input_gdf.iterrows():
            bounds = row['geometry'].bounds
            tiles = mercantile.tiles(bounds[0], bounds[1], bounds[2], bounds[3], zoom_level)
            resp = []
            for t in tiles:
                r = row.copy()
                geometry = box(*mercantile.bounds(t))
                if geometry.intersects(row['geometry']):
                    r['geometry'] = geometry
                    r['quadkey'] = mercantile.quadkey(t)
                    resp.append(r)

            dfs.append(pd.DataFrame(resp))

        return CartoDataFrame(pd.concat(dfs).reset_index(drop=True), crs='epsg:4326')

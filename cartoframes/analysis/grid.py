import mercantile
import pandas as pd

from shapely.geometry import box
from ..core.cartodataframe import CartoDataFrame


class QuadGrid():

    def polyfill(self, input_gdf, zoom_level):
        if not hasattr(input_gdf, 'geometry'):
            raise ValueError('This dataframe has no valid geometry.')

        geometry_name = input_gdf.geometry.name

        dfs = []
        for _, row in input_gdf.iterrows():
            input_geometry = row[geometry_name]
            bounds = input_geometry.bounds
            tiles = mercantile.tiles(bounds[0], bounds[1], bounds[2], bounds[3], zoom_level)
            new_rows = []
            for tile in tiles:
                new_row = row.copy()
                new_geometry = box(*mercantile.bounds(tile))
                if new_geometry.intersects(input_geometry):
                    new_row[geometry_name] = new_geometry
                    new_row['quadkey'] = mercantile.quadkey(tile)
                    new_rows.append(new_row)
            dfs.append(pd.DataFrame(new_rows))

        df = pd.concat(dfs).reset_index(drop=True)

        return CartoDataFrame(df, geometry=geometry_name, crs='epsg:4326')

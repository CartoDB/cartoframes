from tiletanic.tileschemes import WebMercator
from tiletanic.tilecover import cover_geometry
from shapely.geometry import box
import geopandas as gpd
import pandas as pd

class Grid(object):

    def polyfill_quadkey(input_gdf, zoom_level):
        tiler = WebMercator()
        
        gdf = input_gdf.copy()
        if not gdf.crs or not 'init' in gdf.crs:
            # assuming 4326 if not specified
            gdf.crs = {'init': 'epsg:4326'}
        
        gdf = gdf.to_crs({'init': 'epsg:3857'})
        
        dfs = []
        
        for row_id, row in gdf.iterrows():
            tiles = cover_geometry(tiler, row['geometry'], zoom_level)
            
            resp = []
            for t in tiles:
                r = row.copy()
                r['geometry'] = box(*tiler.bbox(t))
                r['quadkey'] = tiler.quadkey(t)
                resp.append(r)

            dfs.append(pd.DataFrame(resp))
        
        r_gdf = gpd.GeoDataFrame(pd.concat(dfs).reset_index(drop=True))
        r_gdf.crs = {'init': 'epsg:3857'}
        return r_gdf.to_crs({'init': 'epsg:4326'})
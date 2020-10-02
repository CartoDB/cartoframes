from geopandas import GeoDataFrame
from ...clients.bigquery_client import BigQueryClient
from ....utils.geom_utils import set_geometry

GEOM_COLUMN_NAME = 'geom'


def compute_placekey_geom(dataframe, placekey_col='placekey'):
    bq = BigQueryClient()
    placekeys = ['\'{}\''.format(p) for p in dataframe[placekey_col]]
    query = '''
    SELECT p AS {0}, jslibs.placekey.ST_GEOGPOINTFROMPLACEKEY(p) AS {1}
    FROM UNNEST([{2}]) AS p
    '''.format(placekey_col, GEOM_COLUMN_NAME, ','.join(placekeys))
    job = bq.query(query)
    geom_dataframe = bq.download_to_dataframe(job)
    gdf = GeoDataFrame(dataframe.merge(geom_dataframe, on=placekey_col), crs='epsg:4326')
    set_geometry(gdf, GEOM_COLUMN_NAME, inplace=True)
    return gdf

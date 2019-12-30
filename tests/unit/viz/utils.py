from geopandas import GeoDataFrame
from cartoframes.utils import set_geometry_from_xy


def build_geodataframe(lats, lngs, extra_columns=[]):
    columns = {'lat': lats, 'lng': lngs}
    for extra_column in extra_columns:
        columns[extra_column] = lats
    return set_geometry_from_xy(GeoDataFrame(columns), 'lng', 'lat')

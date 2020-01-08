from geopandas import GeoDataFrame, points_from_xy


def build_geodataframe(lats, lngs, extra_columns=[]):
    columns = {'lat': lats, 'lng': lngs}
    for extra_column in extra_columns:
        columns[extra_column] = lats
    return GeoDataFrame(columns, geometry=points_from_xy(columns['lng'], columns['lat']))

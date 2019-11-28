from cartoframes import CartoDataFrame


def build_cartodataframe(lats, lngs, extra_columns=[]):
    columns = {'lat': lats, 'lng': lngs}
    for extra_column in extra_columns:
        columns[extra_column] = lats
    return CartoDataFrame(columns).set_geometry_from_xy('lng', 'lat')

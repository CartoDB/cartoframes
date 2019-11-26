from pandas import DataFrame

from cartoframes import CartoDataFrame


def build_geodataframe(lats, lngs, extra_columns=[]):
    columns = {
        'latitude': lats,
        'longitude': lngs
    }
    for extra_column in extra_columns:
        columns[extra_column] = lats

    return CartoDataFrame(columns).convert()


def simple_dataframe(extra_columns=[]):
    default_data = [0]
    columns = {'lat': default_data, 'lng': default_data}

    for extra_column in extra_columns:
        columns[extra_column] = default_data

    return DataFrame(columns)

from pandas import DataFrame

from cartoframes.utils.geom_utils import geodataframe_from_dataframe


def build_geodataframe(lats, lngs):
    coordinates = {
        'latitude': lats,
        'longitude': lngs
    }

    dataframe = DataFrame(coordinates)

    return geodataframe_from_dataframe(dataframe)


def simple_dataframe():
    return DataFrame({'lat': [0], 'lng': [0]})

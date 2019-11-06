from pandas import DataFrame

from cartoframes.utils.geom_utils import geodataframe_from_dataframe


def build_geojson(lats, lngs):
    coordinates = {
        'latitude': lats,
        'longitude': lngs
    }

    dataframe = DataFrame(coordinates)

    return geodataframe_from_dataframe(dataframe)

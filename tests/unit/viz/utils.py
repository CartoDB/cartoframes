from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely.geometry import Point


def build_geojson(lats, lngs):
    coordinates = {
        'Latitude': lats,
        'Longitude': lngs
    }

    dataframe = DataFrame(coordinates)
    dataframe['Coordinates'] = list(zip(dataframe.Longitude, dataframe.Latitude))
    dataframe['Coordinates'] = dataframe['Coordinates'].apply(Point)

    return GeoDataFrame(dataframe, geometry='Coordinates')


def simple_dataframe():
    return DataFrame({'lat': [0], 'lng': [0]})

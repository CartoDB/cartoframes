from pandas import DataFrame
from geopandas import GeoDataFrame
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

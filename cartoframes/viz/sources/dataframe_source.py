from pandas import DataFrame
from geopandas import GeoDataFrame

from .base_source import BaseSource
from ...utils.geom_utils import set_geometry, has_geometry
from ...utils.utils import get_geodataframe_data, get_geodataframe_bounds, get_geodataframe_geom_type, \
                           get_datetime_column_names

SOURCE_TYPE = 'GeoJSON'

RFC_2822_DATETIME_FORMAT = "%a, %d %b %Y %T %z"


class DataFrameSource(BaseSource):
    """DataFrameSource

    Args:
        df (pandas.DataFrame, geopandas.GeoDataFrame): DataFrame or GeoDataFrame instance.
        geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.

    Example:

        DataFrame object.

        >>> DataFrameSource(df, geom_col='my_geom')

        GeoDataFrame object.

        >>> DataFrameSource(gdf)

    """
    def __init__(self, df, geom_col=None, encode_data=True):
        self.datetime_column_names = None
        self.encode_data = encode_data

        if not isinstance(df, DataFrame):
            raise ValueError('Wrong source input. Valid values are str, dict and DataFrame.')

        self.type = SOURCE_TYPE
        self.gdf = GeoDataFrame(df, copy=True)
        self.set_datetime_columns()

        if geom_col in self.gdf:
            set_geometry(self.gdf, geom_col, inplace=True)
        elif has_geometry(df):
            self.gdf.set_geometry(df.geometry.name, inplace=True)
        else:
            raise ValueError('No valid geometry found. Please provide an input source with ' +
                             'a valid geometry or specify the "geom_col" param with a geometry column.')

    def set_datetime_columns(self):
        self.datetime_column_names = get_datetime_column_names(self.gdf)
        if self.datetime_column_names:
            for column in self.datetime_column_names:
                self.gdf[column] = self.gdf[column].dt.strftime(RFC_2822_DATETIME_FORMAT)

    def get_datetime_column_names(self):
        return self.datetime_column_names

    def get_geom_type(self):
        return get_geodataframe_geom_type(self.gdf)

    def compute_metadata(self, columns=None):
        if columns is not None:
            columns += [self.gdf.geometry.name]
            self.gdf = self.gdf[columns]
        self.data = get_geodataframe_data(self.gdf, self.encode_data)
        self.bounds = get_geodataframe_bounds(self.gdf)

    def is_local(self):
        return True

    def is_public(self):
        return True

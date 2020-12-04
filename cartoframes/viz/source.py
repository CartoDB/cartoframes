from pandas import DataFrame
from geopandas import GeoDataFrame

from ..io.managers.context_manager import ContextManager
from ..utils.geom_utils import is_reprojection_needed, reproject, has_geometry, set_geometry
from ..utils.utils import get_geodataframe_data, get_geodataframe_bounds, \
                          get_geodataframe_geom_type, get_datetime_column_names

RFC_2822_DATETIME_FORMAT = "%a, %d %b %Y %T %z"

VALID_GEOMETRY_TYPES = [
    {'Point'},
    {'MultiPoint'},
    {'LineString'},
    {'MultiLineString'},
    {'LineString', 'MultiLineString'},
    {'Polygon'},
    {'MultiPolygon'},
    {'Polygon', 'MultiPolygon'}
]


class SourceType:
    QUERY = 'Query'
    GEOJSON = 'GeoJSON'


class Source:
    """Source

    Args:
        source (str, pandas.DataFrame, geopandas.GeoDataFrame): a table name,
            SQL query, DataFrame, GeoDataFrame instance.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. If not provided, the credentials will be automatically
            obtained from the default credentials if available.
        geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
        encode_data (bool, optional): Indicates whether the data needs to be encoded.
            Default is True.

    Example:

        Table name.

        >>> Source('table_name')

        SQL query.

        >>> Source('SELECT * FROM table_name')

        DataFrame object.

        >>> Source(df, geom_col='my_geom')

        GeoDataFrame object.

        >>> Source(gdf)

        Setting the credentials.

        >>> Source('table_name', credentials)

    """
    def __init__(self, source, credentials=None, geom_col=None, encode_data=True):
        self.credentials = None
        self.datetime_column_names = None
        self.encode_data = encode_data

        if isinstance(source, str):
            # Table, SQL query
            self.type = SourceType.QUERY
            self.manager = ContextManager(credentials)
            self.query = self.manager.compute_query(source)
            self.credentials = self.manager.credentials
        elif isinstance(source, DataFrame):
            if isinstance(source, GeoDataFrame):
                if is_reprojection_needed(source):
                    source = reproject(source)

            # DataFrame, GeoDataFrame
            self.type = SourceType.GEOJSON
            self.gdf = GeoDataFrame(source, copy=True)
            self.set_datetime_columns()

            if geom_col in self.gdf:
                set_geometry(self.gdf, geom_col, inplace=True)
            elif has_geometry(source):
                self.gdf.set_geometry(source.geometry.name, inplace=True)
            else:
                raise ValueError('No valid geometry found. Please provide an input source with ' +
                                 'a valid geometry or specify the "geom_col" param with a geometry column.')

            # Remove nan geometries
            self.gdf.dropna(subset=[self.gdf.geometry.name], inplace=True)

            # Remove empty geometries
            self.gdf = self.gdf[~self.gdf.geometry.is_empty]

            # Checking the uniqueness of the geometry type
            geometry_types = set(self.gdf.geom_type.unique()).difference({None})
            if geometry_types not in VALID_GEOMETRY_TYPES:
                raise ValueError('No valid geometry column types ({}), it has '.format(geometry_types) +
                                 'to be one of the next type sets: {}.'.format(VALID_GEOMETRY_TYPES))

        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    def get_credentials(self):
        if self.type == SourceType.QUERY:
            if self.credentials:
                return {
                    # CARTO VL requires a username but CARTOframes allows passing only the base_url.
                    # That's why 'user' is used by default if username is empty.
                    'username': self.credentials.username or 'user',
                    'api_key': self.credentials.api_key,
                    'base_url': self.credentials.base_url
                }
        elif self.type == SourceType.GEOJSON:
            return None

    def set_datetime_columns(self):
        if self.type == SourceType.GEOJSON:
            self.datetime_column_names = get_datetime_column_names(self.gdf)

            if self.datetime_column_names:
                for column in self.datetime_column_names:
                    self.gdf[column] = self.gdf[column].dt.strftime(RFC_2822_DATETIME_FORMAT)

    def get_datetime_column_names(self):
        return self.datetime_column_names

    def get_geom_type(self):
        if self.type == SourceType.QUERY:
            return self.manager.get_geom_type(self.query) or 'point'
        elif self.type == SourceType.GEOJSON:
            return get_geodataframe_geom_type(self.gdf)

    def compute_metadata(self, columns=None):
        if self.type == SourceType.QUERY:
            self.data = self.query
            self.bounds = self.manager.get_bounds(self.query)
        elif self.type == SourceType.GEOJSON:
            if columns is not None:
                columns += [self.gdf.geometry.name]
                self.gdf = self.gdf[columns]
            self.data = get_geodataframe_data(self.gdf, self.encode_data)
            self.bounds = get_geodataframe_bounds(self.gdf)

    def is_local(self):
        return self.type == SourceType.GEOJSON

    def is_public(self):
        if self.type == SourceType.QUERY:
            return self.manager.is_public(self.query)
        elif self.type == SourceType.GEOJSON:
            return True

    def schema(self):
        if self.type == SourceType.QUERY:
            return self.manager.get_schema()
        elif self.type == SourceType.GEOJSON:
            return None

    def get_table_names(self):
        if self.type == SourceType.QUERY:
            return self.manager.get_table_names(self.query)
        elif self.type == SourceType.GEOJSON:
            return []

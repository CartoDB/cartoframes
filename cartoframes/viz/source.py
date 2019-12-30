from pandas import DataFrame
from geopandas import GeoDataFrame

from ..utils.managers.context_manager import ContextManager
from ..utils.geom_utils import set_geometry, has_geometry
from ..utils.utils import encode_geodataframe, get_geodataframe_bounds, get_geodataframe_geom_type


class SourceType:
    QUERY = 'Query'
    GEOJSON = 'GeoJSON'


class Source:
    """Source

    Args:
        data (str, pandas.DataFrame, geopandas.GeoDataFrame): a table name,
            SQL query, DataFrame, GeoDataFrame instance.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. If not provided, the credentials will be automatically
            obtained from the default credentials if available.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
            keys, or an array of floats in the following structure: [[west,
            south], [east, north]]. If not provided the bounds will be automatically
            calculated to fit all features.
        geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.

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
    def __init__(self, source, credentials=None, geom_col=None):
        self.credentials = None

        if isinstance(source, str):
            # Table, SQL query
            self.type = SourceType.QUERY
            self.manager = ContextManager(credentials)
            self.query = self.manager.compute_query(source)
            self.credentials = self.manager.credentials
        elif isinstance(source, DataFrame):
            # DataFrame, GeoDataFrame
            self.type = SourceType.GEOJSON
            self.gdf = GeoDataFrame(source, copy=True)

            if geom_col in self.gdf:
                set_geometry(self.gdf, geom_col, inplace=True)

            if not has_geometry(self.gdf):
                raise Exception('No valid geometry found. Please provide an input source with ' +
                                'a valid geometry or specify the "geom_col" param with a geometry column.')
        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    def get_credentials(self):
        if self.credentials:
            return {
                # CARTO VL requires a username but CARTOframes allows passing only the base_url.
                # That's why 'user' is used by default if username is empty.
                'username': self.credentials.username or 'user',
                'api_key': self.credentials.api_key,
                'base_url': self.credentials.base_url
            }

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
            self.data = encode_geodataframe(self.gdf)
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

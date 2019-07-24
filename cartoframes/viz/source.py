from __future__ import absolute_import

import pandas

from . import defaults

from ..data import Dataset
from ..utils import get_query_bounds, get_geodataframe_bounds, encode_geodataframe, \
    is_sql_query, is_geojson_file

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


class SourceType:
    QUERY = 'Query'
    GEOJSON = 'GeoJSON'


class Source(object):
    """Source

    Args:
        data (str, geopandas.GeoDataFrame, pandas.DataFrame,
          :py:class:`Dataset <cartoframes.data.Dataset>` ): a table name,
          SQL query, GeoJSON file, GeoDataFrame, DataFrame, or Dataset object.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
          A Credentials instance. If not provided, the credentials will be automatically
          obtained from the default credentials if available.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
          keys, or an array of floats in the following structure: [[west,
          south], [east, north]]. If not provided the bounds will be automatically
          calculated to fit all features.

    Example:

        Table name.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('table_name')

        SQL query.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('SELECT * FROM table_name')

        GeoJSON file.

        .. code::

            from cartoframes.viz import Source

            Source('path/to/file.geojson')

        Dataset object.

        .. code::

            from cartoframes.viz import Source
            from cartoframes.data import Dataset

            ds = Dataset('table_name')

            Source(ds)

        Setting the credentials.

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.viz import Source

            credentials = Credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('table_name', credentials)

        Setting the bounds.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            bounds = {
                'west': -10,
                'east': 10,
                'north': -10,
                'south': 10
            }

            Source('table_name', bounds=bounds)
    """

    def __init__(self, data, credentials=None, bounds=None, schema=None):
        self._init_source(data, credentials, bounds, schema)

    def get_geom_type(self):
        return self.dataset.compute_geom_type() or Dataset.GEOM_TYPE_POINT

    def get_credentials(self):
        credentials = self.dataset.credentials
        if credentials:
            return {
                # CARTO VL requires a username but CARTOframes allows passing only the base_url.
                # That's why 'user' is used by default if username is empty.
                'username': credentials.username or 'user',
                'api_key': credentials.api_key,
                'base_url': credentials.base_url
            }
        else:
            return defaults.CREDENTIALS

    def _init_source(self, data, credentials, bounds, schema):
        if isinstance(data, str):
            if is_sql_query(data):
                self._init_source_query(data, credentials, bounds)

            elif is_geojson_file(data):
                self._init_source_geojson(data, bounds)

            else:
                self._init_source_query(data, credentials, bounds, schema)

        elif isinstance(data, (list, dict)):
            self._init_source_geojson(data, bounds)

        elif HAS_GEOPANDAS and isinstance(data, geopandas.GeoDataFrame):
            self._init_source_geojson(data, bounds)

        elif isinstance(data, pandas.DataFrame):
            self._init_source_geojson(data, bounds)

        elif isinstance(data, Dataset):
            self._init_source_dataset(data, bounds)

        else:
            raise ValueError('Wrong source input')

    def _init_source_query(self, data, credentials, bounds, schema=None):
        self.dataset = Dataset(data, credentials, schema)
        self._set_source_query(self.dataset, bounds)

    def _init_source_geojson(self, data, bounds):
        self.dataset = Dataset(data)
        self._set_source_geojson(self.dataset, bounds)

    def _init_source_dataset(self, data, bounds):
        self.dataset = data
        if self.dataset.is_local():
            self._set_source_geojson(self.dataset, bounds)
        else:
            self._set_source_query(self.dataset, bounds)

    def _set_source_query(self, dataset, bounds):
        self.type = SourceType.QUERY
        query = dataset.get_query()
        self.query = query
        self.bounds = bounds or self._compute_query_bounds(dataset, query)

    def _set_source_geojson(self, dataset, bounds):
        self.type = SourceType.GEOJSON
        gdf = dataset.get_geodataframe()
        self.query = encode_geodataframe(gdf)
        self.bounds = bounds or self._compute_geojson_bounds(gdf)

    def _compute_query_bounds(self, dataset, query):
        context = dataset._strategy._context
        return get_query_bounds(context, query)

    def _compute_geojson_bounds(self, gdf):
        return get_geodataframe_bounds(gdf)

from __future__ import absolute_import

import pandas

from ..io.context import ContextManager
from ..core.cartodataframe import CartoDataFrame
from ..utils.utils import encode_geodataframe, get_geodataframe_bounds, get_geodataframe_geom_type


class SourceType:
    QUERY = 'Query'
    GEOJSON = 'GeoJSON'


class Source(object):
    """Source

    Args:
        data (str, pandas.DataFrame, geopandas.GeoDataFrame,
          :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>` ): a table name,
          SQL query, DataFrame, GeoDataFrame or CartoDataFrame instance.
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

            set_default_credentials('your_user_name', 'your api key')

            Source('table_name')

        SQL query.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials('your_user_name', 'your api key')

            Source('SELECT * FROM table_name')

        CartoDataFrame object.

        .. code::

            from cartoframes.viz import Source
            from cartoframes.data import CartoDataFrame

            set_default_credentials('your_user_name', 'your api key')

            cdf = CartoDataFrame('table_name')

            Source(cdf)

        Setting the credentials.

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.viz import Source

            credentials = Credentials('your_user_name', 'your api key')

            Source('table_name', credentials)
    """

    def __init__(self, source, credentials=None, schema=None):
        self._credentials = credentials

        if isinstance(source, str):
            # Table, SQL query
            self.type = SourceType.QUERY
            self._manager = ContextManager(credentials)
            self._query = self._manager.compute_query(source, schema)
        elif isinstance(source, pandas.DataFrame):
            # DataFrame, GeoDataFrame, CartoDataFrame
            self.type = SourceType.GEOJSON
            self._cdf = CartoDataFrame(source, copy=True)
        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    def get_credentials(self):
        if hasattr(self, '_manager') and self._manager.credentials:
            return {
                # CARTO VL requires a username but CARTOframes allows passing only the base_url.
                # That's why 'user' is used by default if username is empty.
                'username': self._manager.credentials.username or 'user',
                'api_key': self._manager.credentials.api_key,
                'base_url': self._manager.credentials.base_url
            }

    def get_geom_type(self):
        if self.type == SourceType.QUERY:
            return self._manager.get_geom_type(self._query) or 'point'
        elif self.type == SourceType.GEOJSON:
            return get_geodataframe_geom_type(self._cdf)

    def compute_metadata(self, columns=None):
        if self.type == SourceType.QUERY:
            self.data = self._query
            self.bounds = self._manager.get_bounds(self._query)
        elif self.type == SourceType.GEOJSON:
            self._cdf = self._cdf[columns] if columns is not None else self._cdf
            self.data = encode_geodataframe(self._cdf)
            self.bounds = get_geodataframe_bounds(self._cdf)
            del self._cdf

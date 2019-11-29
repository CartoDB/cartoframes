from __future__ import absolute_import

import pandas

from ..core.cartodataframe import CartoDataFrame
from ..core.managers.context_manager import ContextManager
from ..utils.utils import encode_geodataframe, get_geodataframe_bounds, get_geodataframe_geom_type


class SourceType:
    QUERY = 'Query'
    GEOJSON = 'GeoJSON'


class Source(object):
    """Source

    Args:
        data (str, pandas.DataFrame, geopandas.GeoDataFrame,
          :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>` ): a table name,
          SQL query, DataFrame, GeoDataFrame or CartoDataFrame instance.
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
            from cartoframes import CartoDataFrame

            set_default_credentials('your_user_name', 'your api key')

            cdf = CartoDataFrame.from_carto('table_name')

            Source(cdf)

        Setting the credentials.

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.viz import Source

            credentials = Credentials('your_user_name', 'your api key')

            Source('table_name', credentials)
    """

    def __init__(self, source, credentials=None, geom_col=None):
        self.credentials = None

        if isinstance(source, str):
            # Table, SQL query
            self.type = SourceType.QUERY
            self.manager = ContextManager(credentials)
            self.query = self.manager.compute_query(source)
            self.credentials = self.manager.credentials
        elif isinstance(source, pandas.DataFrame):
            # DataFrame, GeoDataFrame, CartoDataFrame
            self.type = SourceType.GEOJSON
            self.cdf = CartoDataFrame(source, copy=True)

            if geom_col:
                self.cdf.set_geometry(geom_col, inplace=True)

            if not self.cdf.has_geometry():
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
            return get_geodataframe_geom_type(self.cdf)

    def compute_metadata(self, columns=None):
        if self.type == SourceType.QUERY:
            self.data = self.query
            self.bounds = self.manager.get_bounds(self.query)
        elif self.type == SourceType.GEOJSON:
            if columns is not None:
                columns += [self.cdf.geometry.name]
                self.cdf = self.cdf[columns]
            self.data = encode_geodataframe(self.cdf)
            self.bounds = get_geodataframe_bounds(self.cdf)

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

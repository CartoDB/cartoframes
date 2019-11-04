from __future__ import absolute_import

from . import defaults
from ..data import CartoDataFrame
from ..utils.geom_utils import geodataframe_from_dataframe
from ..utils.utils import get_query_bounds, get_geodataframe_bounds, encode_geodataframe


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

        Setting the bounds.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials('your_user_name', 'your api key')

            bounds = {
                'west': -10,
                'east': 10,
                'north': -10,
                'south': 10
            }

            Source('table_name', bounds=bounds)
    """

    def __init__(self, data, credentials=None, bounds=None, schema=None):
        if isinstance(data, CartoDataFrame):
            self.cdf = data
        else:
            self.cdf = CartoDataFrame(data, credentials=credentials, schema=schema, download=False)

        self._init_source_cdf(bounds)

    def get_geom_type(self):
        return self.cdf.geom_type() or 'point'

    def get_credentials(self):
        credentials = self.cdf._strategy.credentials
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

    def _init_source_cdf(self, bounds):
        if self.cdf.is_local():
            gdf = geodataframe_from_dataframe(self.cdf)
            self.type = SourceType.GEOJSON
            self.data = encode_geodataframe(gdf)
            self.bounds = bounds or self._compute_geojson_bounds(gdf)
        else:
            self.type = SourceType.QUERY
            self.data = self.cdf.get_query()
            self.bounds = bounds or self._compute_query_bounds()

    def _compute_geojson_bounds(self, gdf):
        return get_geodataframe_bounds(gdf)

    def _compute_query_bounds(self):
        context = self.cdf._strategy._context
        return get_query_bounds(context, self.data)

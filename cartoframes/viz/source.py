from __future__ import absolute_import

from ..data import CartoDataFrame
from ..utils.utils import get_query_bounds, get_geodataframe_bounds, encode_geodataframe
from ..utils.geom_utils import geodataframe_from_dataframe, reset_geodataframe


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

    def __init__(self, data, credentials=None, schema=None):
        if isinstance(data, CartoDataFrame):
            self.cdf = data
        else:
            self.cdf = CartoDataFrame(data, credentials=credentials, schema=schema, download=False)

    def get_geom_type(self):
        return self.cdf.geom_type() or 'point'
        # if not self._df.empty and 'geometry' in self._df and len(self._df.geometry) > 0:
        #     geometry = _first_value(self._df.geometry)
        #     if geometry and geometry.geom_type:
        #         return map_geom_type(geometry.geom_type)
        # return None

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

    def compute_metadata(self, columns=None):
        if self.cdf.is_local():
            gdf = geodataframe_from_dataframe(self.cdf)
            gdf = gdf[columns] if columns is not None else gdf
            self.type = SourceType.GEOJSON
            self.data = self._compute_geojson_data(gdf)
            self.bounds = self._compute_geojson_bounds(gdf)
            reset_geodataframe(self.cdf)
        else:
            self.type = SourceType.QUERY
            self.data = self._compute_query_data()
            self.bounds = self._compute_query_bounds()

    def _compute_query_data(self):
        return self.cdf.get_query()

    def _compute_query_bounds(self):
        context = self.cdf._strategy._context
        return get_query_bounds(context, self.data)

    def _compute_geojson_data(self, gdf):
        return encode_geodataframe(gdf)

    def _compute_geojson_bounds(self, gdf):
        return get_geodataframe_bounds(gdf)

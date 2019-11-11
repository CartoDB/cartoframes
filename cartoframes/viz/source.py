from __future__ import absolute_import

from ..data import Dataset
from ..data.dataset.registry.base_dataset import BaseDataset
from ..utils.utils import get_query_bounds, get_geodataframe_bounds, encode_geodataframe
from ..utils.geom_utils import compute_geodataframe, reset_geodataframe


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

            set_default_credentials('your_user_name', 'your api key')

            Source('table_name')

        SQL query.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Source

            set_default_credentials('your_user_name', 'your api key')

            Source('SELECT * FROM table_name')

        GeoJSON file.

        .. code::

            from cartoframes.viz import Source

            Source('path/to/file.geojson')

        Dataset object.

        .. code::

            from cartoframes.viz import Source
            from cartoframes.data import Dataset

            set_default_credentials('your_user_name', 'your api key')

            ds = Dataset('table_name')

            Source(ds)

        Setting the credentials.

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.viz import Source

            credentials = Credentials('your_user_name', 'your api key')

            Source('table_name', credentials)
    """

    def __init__(self, data, credentials=None, schema=None):
        if isinstance(data, Dataset):
            self.dataset = data
        else:
            self.dataset = Dataset(data, credentials, schema)

    def get_geom_type(self):
        return self.dataset.compute_geom_type() or BaseDataset.GEOM_TYPE_POINT

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

    def compute_metadata(self, columns=None):
        if self.dataset.is_local():
            gdf = compute_geodataframe(self.dataset)
            gdf = gdf[columns] if columns is not None else gdf
            self.type = SourceType.GEOJSON
            self.data = self._compute_geojson_data(gdf)
            self.bounds = self._compute_geojson_bounds(gdf)
            reset_geodataframe(self.dataset)
        else:
            self.type = SourceType.QUERY
            self.data = self._compute_query_data()
            self.bounds = self._compute_query_bounds()

    def _compute_query_data(self):
        return self.dataset.get_query()

    def _compute_query_bounds(self):
        context = self.dataset._strategy._context
        return get_query_bounds(context, self.data)

    def _compute_geojson_data(self, gdf):
        return encode_geodataframe(gdf)

    def _compute_geojson_bounds(self, gdf):
        return get_geodataframe_bounds(gdf)

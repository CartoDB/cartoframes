from __future__ import absolute_import

import re
import pandas

from . import defaults
from ..geojson import get_encoded_data, get_bounds
from ..data import Dataset, is_sql_query, is_geojson_file

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
        context (:py:class:`Context <cartoframes.auth.Context>`):
          A Context instance. If not provided the context will be automatically
          obtained from the default context if available.
        bounds (dict or list): a dict with `east`, `north`, `west`, `south`
          keys, or a list of floats in the following order: [west,
          south, east, north]. If not provided the bounds will be automatically
          calculated to fit all features.

    Example:

        Table name.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Source

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('table_name')

        SQL query.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Source

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('SELECT * FROM table_name')

        GeoJSON file.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Source

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('path/to/file.geojson')

        Dataset object.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Source
            from cartoframes.data import Dataset

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            ds = Dataset('table_name')

            Source(ds)

        Setting the context.

        .. code::

            from cartoframes.auth import Context
            from cartoframes.viz import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('table_name', context)

        Setting the bounds.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Source

            set_default_context(
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

    def __init__(self, data, context=None, bounds=None, schema=None):
        self._init_source(data, context, bounds, schema)

        self.context = _get_context(self.dataset)
        self.geom_type = _get_geom_type(self.dataset)
        self.credentials = _get_credentials(self.dataset)

    def _init_source(self, data, context, bounds, schema):
        if isinstance(data, str):
            if is_sql_query(data):
                self._init_source_query(data, context, bounds, schema)

            elif is_geojson_file(data):
                self._init_source_geojson(data, bounds)

            elif _check_table_name(data):
                 self._init_source_table(data, context, schema, bounds)

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

    def _init_source_table(self, data, context, bounds, schema):
        self.dataset = Dataset(data, context, schema)
        self._set_source_query(self.dataset, bounds)

    def _init_source_query(self, data, context, bounds):
        self.dataset = Dataset(data, context)
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
        self.query = dataset.get_query()
        self.bounds = bounds

    def _set_source_geojson(self, dataset, bounds):
        self.type = SourceType.GEOJSON
        gdf = dataset.get_geodataframe()
        self.query = get_encoded_data(gdf)
        self.bounds = bounds or get_bounds(gdf)


def _check_table_name(data):
    return True


def _get_context(dataset):
    return dataset.credentials


def _get_credentials(dataset):
    context = _get_context(dataset)
    if context and context.creds:
        return {
            'username': context.creds.username(),
            'api_key': context.creds.key(),
            'base_url': context.creds.base_url()
        }
    else:
        return defaults.CREDENTIALS


def _get_geom_type(dataset):
    return dataset.compute_geom_type() or Dataset.GEOM_TYPE_POINT

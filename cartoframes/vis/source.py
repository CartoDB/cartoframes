from __future__ import absolute_import

import re

from . import defaults
from ..dataset import Dataset
from ..geojson import get_encoded_data, get_bounds

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
        data (str, :py:class:`GeoFrame <geopandas.GeoDataFrame>`,
          :py:class:`Dataset <cartoframes.vis.Dataset>` ): a table name, SQL query
          ,GeoJSON file, GeoFrame object or Dataset object.
        context (:py:class:`Context <cartoframes.Context>`):
          A Conext instance. If not provided the context will be automatically
          obtained from the default context.
        bounds (dict or list): a dict with `east`,`north`,`west`,`south`
          properties, or a list of floats in the following order: [west,
          south, east, north]. If not provided the bounds will be automatically
          calculated to fit all features.

    Example:

        Table name.

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            Source('table_name')

        SQL query.

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            Source('SELECT * FROM table_name')

        GeoJSON file.

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            Source('path/to/file.geojson')

        Dataset object.

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Source
            from cartoframes import Dataset

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            ds = Dataset.from_table('table_name')

            Source(ds)

        Setting the context.

        .. code::

            from cartoframes import Context
            from cartoframes.vis import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Source('table_name', context)

        Setting the bounds.

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Source

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            bounds = {
                'west': -10,
                'east': 10,
                'north': -10,
                'south': 10
            }

            Source('table_name', bounds=bounds)
    """

    def __init__(self, data, context=None, bounds=None, schema='public'):
        if isinstance(data, str):
            if _check_sql_query(data):
                self._init_source_query(data, context, bounds)

            elif _check_geojson_file(data):
                self._init_source_geojson(data, bounds)

            elif _check_table_name(data):
                self._init_source_query(_format_query(data, schema), context, bounds)

        elif HAS_GEOPANDAS and isinstance(data, (list, dict, geopandas.GeoDataFrame)):
            self._init_source_geojson(data, bounds)

        elif isinstance(data, Dataset):
            self._init_source_dataset(data, bounds)

        else:
            raise ValueError('Wrong source input')

        self.context = self.dataset.cc
        self.credentials = _get_credentials(self.context)
        self.geom_type = _get_geom_type(self.dataset)

    def _init_source_query(self, data, context, bounds):
        self.dataset = Dataset.from_query(data, context)
        self.type = SourceType.QUERY
        self.query = self.dataset.query
        self.bounds = bounds

    def _init_source_geojson(self, data, bounds):
        self.dataset = Dataset.from_geojson(data)
        self.type = SourceType.GEOJSON
        self.query = get_encoded_data(self.dataset.gdf)
        self.bounds = bounds or get_bounds(self.dataset.gdf)

    def _init_source_dataset(self, data, bounds):
        self.dataset = data
        self.type = _map_dataset_state(self.dataset.state)

        if self.dataset.state == Dataset.STATE_REMOTE:
            self.bounds = bounds
            if self.dataset.query:
                self.query = self.dataset.query
            else:
                self.query = _format_query(self.dataset.table_name, self.dataset.schema)
        elif self.dataset.state == Dataset.STATE_LOCAL:
            if self.dataset.gdf:
                self.query = get_encoded_data(self.dataset.gdf)
                self.bounds = bounds or get_bounds(self.dataset.gdf)
            else:
                # TODO: Dataframe
                pass


def _check_table_name(data):
    return True


def _check_sql_query(data):
    return re.match(r'^\s*(WITH|SELECT)\s+', data, re.IGNORECASE)


def _check_geojson_file(data):
    return re.match(r'^.*\.geojson\s*$', data, re.IGNORECASE)


def _format_query(table_name, schema='public'):
    return 'SELECT * FROM "{0}"."{1}"'.format(schema, table_name)


def _map_dataset_state(state):
    return {
        Dataset.STATE_REMOTE: SourceType.QUERY,
        Dataset.STATE_LOCAL: SourceType.GEOJSON
    }[state]


def _get_credentials(context):
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

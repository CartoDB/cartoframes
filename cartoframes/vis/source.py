from __future__ import absolute_import

from . import defaults
from ..dataset import Dataset
from ..geojson import get_query_and_bounds

import re
import geopandas


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

    def __init__(self, data, context=None, bounds=None):

        if isinstance(data, str):

            if _check_sql_query(data):
                self.dataset = Dataset.from_query(context, query=data)

            elif _check_geojson_file(data):
                self.dataset = Dataset.from_geojson(None, geodf=data)

            elif _check_table_name(data):
                self.dataset = Dataset.from_table(context, table_name=data)

        elif isinstance(data, geopandas.GeoDataFrame):
            self.dataset = Dataset.from_geojson(None, geodf=data)

        elif isinstance(data, Dataset):
            self.dataset = data

        else:
            raise ValueError('Wrong source input')

        self.type = self.dataset.type
        self.query = self.dataset.get_data()
        self.bounds = bounds
        if self.type == Dataset.GEODATAFRAME_TYPE:
            self.query, self.bounds = get_query_and_bounds(self.dataset.geodf)

        self.context = self.dataset.cc
        if self.dataset.cc and self.dataset.cc.creds:
            self.credentials = {
                'username': self.dataset.cc.creds.username(),
                'api_key': self.dataset.cc.creds.key(),
                'base_url': self.dataset.cc.creds.base_url()
            }
        else:
            self.credentials = defaults._CREDENTIALS


def _check_table_name(data):
    return True


def _check_sql_query(data):
    return re.match(r'^\s*(WITH|SELECT)\s+', data, re.IGNORECASE)


def _check_geojson_file(data):
    return re.match(r'^.*\.geojson\s*$', data, re.IGNORECASE)

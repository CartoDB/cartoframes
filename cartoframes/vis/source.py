from __future__ import absolute_import

from .utils import defaults
from ..dataset import Dataset
from ..geojson import get_query_and_bounds

import re
import geopandas


class Source(object):
    """CARTO VL Source:

      Args:
        - data.
        - bounds (dict): Viewport bounds.
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

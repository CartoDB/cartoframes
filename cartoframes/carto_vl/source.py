from __future__ import absolute_import

from .utils import defaults
from ..dataset import Dataset

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
                self.dataset = Dataset.create_from_query(data, context)

            elif _check_geojson_file(data):
                self.dataset = Dataset.create_from_geojson(data)

            elif _check_table_name(data):
                self.dataset = Dataset.create_from_table(data, context)

        elif isinstance(data, geopandas.GeoDataFrame):
            self.dataset = Dataset.create_from_geojson(data)

        elif isinstance(data, Dataset):
            self.dataset = data

        else:
            raise ValueError('Wrong source input')

        self.bounds = bounds or self.dataset.bounds
        self.type = self.dataset.type
        self.query = self.dataset.query
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
    return re.match(r'^\s*SELECT\s+', data, re.IGNORECASE)


def _check_geojson_file(data):
    return re.match(r'^.*\.geojson\s*$', data, re.IGNORECASE)

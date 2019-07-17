"""Data namespace contains the class to manage your data: Dataset."""
from __future__ import absolute_import

from .dataset import Dataset
from .dataset_info import DatasetInfo
from .data_obs import DataObs
from .utils import is_sql_query, is_geojson_file
from .registry.strategies_registry import StrategiesRegistry

__all__ = [
    'Dataset',
    'DatasetInfo',
    'DataObs'
    'is_sql_query',
    'is_geojson_file',
    'StrategiesRegistry'
]

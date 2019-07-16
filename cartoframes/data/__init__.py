"""Data namespace contains the class to manage your data: Dataset."""
from __future__ import absolute_import

from .dataset import Dataset
from .dataset_info import DatasetInfo
from .utils import is_sql_query, is_geojson_file, is_geojson_file_path
from .registry.strategy_registry import StrategiesRegistry

__all__ = [
    'Dataset',
    'DatasetInfo',
    'is_sql_query',
    'is_geojson_file',
    'is_geojson_file_path',
    'StrategiesRegistry'
]

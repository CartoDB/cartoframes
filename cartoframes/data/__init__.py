"""Data namespace contains the class to manage your data: Dataset."""
from __future__ import absolute_import

from .dataset import Dataset, get_query, get_geodataframe
from .dataset_info import DatasetInfo

__all__ = [
    'Dataset',
    'DatasetInfo',
    'get_query',
    'get_geodataframe'
]

# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.data import StrategiesRegistry
from cartoframes.data.dataset.registry.dataframe_dataset import DataFrameDataset
from cartoframes.data.dataset.registry.query_dataset import QueryDataset
from cartoframes.data.dataset.registry.table_dataset import TableDataset
from cartoframes.data.dataset.registry.base_dataset import BaseDataset
from cartoframes.data.dataset.dataset_info import DatasetInfo
from cartoframes.data import Dataset


class MetadataMock():
    def __init__(self):
        self.privacy = Dataset.PRIVACY_PRIVATE
        self.name = None


class DatasetInfoMock(DatasetInfo):
    def _get_metadata(self, _1, _2):
        return MetadataMock()

    def _save_metadata(self):
        return True


class DataFrameDatasetMock(DataFrameDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _get_dataset_info(self, table_name=None):
        return DatasetInfoMock(self._credentials, table_name or self._table_name)

    def _create_table(self, _):
        return True

    def _copyfrom(self, _, _2):
        return True

    def compute_geom_type(self):
        return BaseDataset.GEOM_TYPE_POINT


class QueryDatasetMock(QueryDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _create_table_from_query(self):
        return True

    def _copyto(self, _, _2, _3, _4, _5):
        self._df = pd.DataFrame({'column_name': [1]})
        return self._df

    def _get_query_columns(self):
        return True

    def compute_geom_type(self):
        return BaseDataset.GEOM_TYPE_POINT

    def _get_read_query(self, table_columns, limit=None):
        return self._query


class TableDatasetMock(TableDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _get_dataset_info(self, table_name=None):
        return DatasetInfoMock(self._credentials, table_name or self._table_name)

    def _copyto(self, _, _2, _3, _4, _5):
        self._df = pd.DataFrame({'column_name': [1]})
        return self._df

    def _get_table_columns(self):
        return True

    def _get_read_query(self, _, _2):
        return True

    def compute_geom_type(self):
        return BaseDataset.GEOM_TYPE_POINT


class StrategiesRegistryMock(StrategiesRegistry):
    def _get_initial_strategies(self):
        return [DataFrameDatasetMock, QueryDatasetMock, TableDatasetMock]


class DatasetMock(Dataset):
    def _get_strategies_registry(self):
        return StrategiesRegistryMock()

    def compute_geom_type(self):
        return BaseDataset.GEOM_TYPE_POINT

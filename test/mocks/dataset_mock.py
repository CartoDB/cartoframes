# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.data.registry.strategies_registry import StrategiesRegistry
from cartoframes.data.registry.dataframe_dataset import DataFrameDataset
from cartoframes.data.registry.query_dataset import QueryDataset
from cartoframes.data.registry.table_dataset import TableDataset
from cartoframes.data import Dataset, DatasetInfo


class MetadataMock():
    def __init__(self):
        self.privacy = DatasetInfo.PRIVATE
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

    def _create_table(self, _, _2):
        return True

    def _copyfrom(self, _, _2):
        return True

    def compute_geom_type(self):
        return Dataset.GEOM_TYPE_POINT


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
        return Dataset.GEOM_TYPE_POINT

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
        return Dataset.GEOM_TYPE_POINT


class StrategiesRegistryMock(StrategiesRegistry):
    def _get_initial_strategies(self):
        return [DataFrameDatasetMock, QueryDatasetMock, TableDatasetMock]


class DatasetMock(Dataset):
    def _get_strategies_registry(self):
        return StrategiesRegistryMock()

    def _set_strategy(self, strategy, data, credentials=None, schema=None):
        if strategy == DataFrameDataset:
            strategy = DataFrameDatasetMock
        elif strategy == TableDataset:
            strategy = TableDatasetMock
        elif strategy == QueryDataset:
            strategy = QueryDatasetMock

        super(DatasetMock, self)._set_strategy(strategy, data, credentials, schema)

    def compute_geom_type(self):
        return Dataset.GEOM_TYPE_POINT

# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.data.dataframe_dataset import DataFrameDataset
from cartoframes.data.query_dataset import QueryDataset
from cartoframes.data.table_dataset import TableDataset
from cartoframes.data import Dataset, DatasetInfo
from mocks.context_mock import ContextMock


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


class TableDatasetMock(TableDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _get_dataset_info(self):
        return DatasetInfoMock(self._context, self._table_name)

    def _copyto(self, _, _2, _3, _4, _5):
        self._df = pd.DataFrame({'column_name': [1]})
        return self._df

    def _get_table_columns(self):
        return True

    def _get_read_query(self, _, _2):
        return True

    def compute_geom_type(self):
        return Dataset.GEOM_TYPE_POINT


class DatasetMock(Dataset):
    def _getDataFrameDataset(self, data):
        return DataFrameDatasetMock(data)

    def _getQueryDataset(self, data, context):
        return QueryDatasetMock(data, context)

    def _getTableDataset(self, data, context, schema):
        return TableDatasetMock(data, context, schema)

    def _set_strategy(self, strategy, data, context=None, schema=None):
        if strategy == DataFrameDataset:
            strategy = DataFrameDatasetMock
        elif strategy == TableDataset:
            strategy = TableDatasetMock
        elif strategy == QueryDataset:
            strategy = QueryDatasetMock

        super(DatasetMock, self)._set_strategy(strategy, data, context, schema)

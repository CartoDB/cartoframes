# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.data.dataset_base import DatasetBase
from cartoframes.data.dataframe_dataset import DataFrameDataset
from cartoframes.data.query_dataset import QueryDataset
from cartoframes.data.table_dataset import TableDataset
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


class QueryDatasetMock(QueryDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _create_table_from_query(self):
        return True


class TableDatasetMock(TableDataset):
    def _create_client(self):
        return None

    def exists(self):
        return False

    def _get_dataset_info(self):
        return DatasetInfoMock(self._context, self._table_name)


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

    def download(self):
        self._df = pd.DataFrame({'column_name': [1]})
        return self._df

    def _copyfrom(self, _):
        return True

    def _create_table(self, _):
        return True

    def compute_geom_type(self):
        return Dataset.GEOM_TYPE_POINT

from abc import ABCMeta

from .dataframe_dataset import DataFrameDataset
from .query_dataset import QueryDataset
from .table_dataset import TableDataset
from ..geojson import load_geojson


class Dataset(object):
    def __init__(self, data, context=None, schema=None):
        self._strategy = self._get_strategy(data)

    def _get_strategy(self, data):
        if isinstance(data, pd.DataFrame):
            return DataFrameDataset(data)
        elif isinstance(data, str):
            if _is_sql_query(data):
                if not context:
                    raise ValueError('QueryDataset needs a Context object')
                return QueryDataset(data, context)
            elif _is_geojson_file_path(data) or isinstance(data, (list, dict)):
                return DataFrameDataset(load_geojson(data))
            else:
                if not context:
                    raise ValueError('TableDataset needs a Context object')
                return TableDataset(data, context, schema)
        else:
            raise ValueError('We can not detect the Dataset type')

    def _set_strategy(self, strategy, data):
        self._strategy = strategy(data)

    def download(self):
        self._strategy.download()
        self._set_strategy(DataFrameDataset, data)
        return self._strategy.dataframe

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, context=None):
        if table_name:
            self._strategy.table_name = table_name
        if context:
            self._strategy.context = context
        if schema:
            self._strategy.schema = schema

        self._strategy.upload(with_lnglat, if_exists)


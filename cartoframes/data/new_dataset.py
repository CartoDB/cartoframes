from abc import ABCMeta

from .dataframe_dataset import DataFrameDataset
from .query_dataset import QueryDataset
from .table_dataset import TableDataset
from ..geojson import load_geojson

DOWNLOAD_RETRY_TIMES = 3


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

    def download(self, limit=None, decode_geom=False, retry_times=DOWNLOAD_RETRY_TIMES):
        data = self._strategy.download(limit, decode_geom, retry_times)
        self._set_strategy(DataFrameDataset, data)
        return data

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, context=None):
        if table_name:
            self._strategy.table_name = table_name
        if context:
            self._strategy.context = context
        if schema:
            self._strategy.schema = schema

        self._strategy.upload(if_exists, with_lnglat)


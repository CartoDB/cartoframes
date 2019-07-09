from abc import ABCMeta

from .dataframe_dataset import DataFrameDataset
from .query_dataset import QueryDataset
from .table_dataset import TableDataset
from ..geojson import load_geojson


class Dataset(object):
    def __init__(self, data):
        self._strategy = self._get_strategy(data)

    def _get_strategy(self, data):
        if isinstance(data, pd.DataFrame):
            return DataFrameDataset(data)
        elif isinstance(data, str):
            if _is_sql_query(data):
                return QueryDataset(data)
            elif _is_geojson_file_path(data) or isinstance(data, (list, dict)):
                return DataFrameDataset(load_geojson(data))
            else:
                return TableDataset(data)
        else:
            raise ValueError('We can not detect the Dataset type')

    def _set_strategy(self, strategy, data):
        self._strategy = strategy(data)

    def download(self):
        data = self._strategy.download()
        self._set_strategy(DataFrameDataset, data)

    def upload(self):
        self._strategy.upload()

















def _is_sql_query(data):
    return re.match(r'^\s*(WITH|SELECT)\s+', data, re.IGNORECASE)


def _is_geojson_file_path(data):
    return isinstance(data, str) and re.match(r'^.*\.geojson\s*$', data, re.IGNORECASE)

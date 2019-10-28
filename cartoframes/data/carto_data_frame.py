from pandas import DataFrame

from .dataset.registry.base_dataset import BaseDataset
from .dataset.registry.table_dataset import TableDataset
from .dataset.registry.query_dataset import QueryDataset
from .dataset.registry.dataframe_dataset import DataFrameDataset

from ..viz import Map, Layer
from ..auth.defaults import get_default_credentials


class CartoDataFrame(DataFrame):

    DOWNLOAD_RETRY_TIMES = 3

    def __init__(self, *args, **kwargs):
        credentials = kwargs.pop('credentials', None)
        super(CartoDataFrame, self).__init__(*args, **kwargs)
        self.credentials = credentials or get_default_credentials()
        self._strategy = DataFrameDataset.create(self, self.credentials)

    @classmethod
    def from_table(cls, table_name, schema='', credentials=None):
        _credentials = credentials or get_default_credentials()
        cdf = cls(credentials=_credentials)
        cdf._strategy = TableDataset.create(table_name, _credentials, schema)
        return cdf

    @classmethod
    def from_query(cls, query, credentials=None):
        _credentials = credentials or get_default_credentials()
        cdf = cls(credentials=_credentials)
        cdf._strategy = QueryDataset.create(query, _credentials)
        return cdf

    @classmethod
    def from_dataframe(cls, dataframe, credentials=None):
        _credentials = credentials or get_default_credentials()
        cdf = cls(credentials=_credentials)
        object.__setattr__(cdf, '_data', dataframe._data)
        cdf._strategy = DataFrameDataset.create(cdf, _credentials)
        return cdf

    def download(self, limit=None, decode_geom=None,
                 retry_times=DOWNLOAD_RETRY_TIMES, credentials=None):
        if self._strategy:
            self._strategy.credentials = credentials or self.credentials
            df = self._strategy.download(limit, decode_geom, retry_times)
            object.__setattr__(self, '_data', df._data)
        return self

    def upload(self, table_name=None, schema=None, with_lnglat=False,
               if_exists=BaseDataset.IF_EXISTS_FAIL, credentials=None):
        if self._strategy:
            if table_name:
                self._strategy.table_name = table_name
            if schema:
                self._strategy.schema = schema
            self._strategy.credentials = credentials or self.credentials
            self._strategy.upload(if_exists, with_lnglat)
            print('Data uploaded successfully!')
        else:
            raise Exception('No strategy defined')

    def plot(self, *args, ** kwargs):
        return Map(Layer(self, *args, **kwargs))

    def delete(self):
        return self._strategy.delete()

    def exists(self):
        return self._strategy.exists()

    def is_public(self):
        return self._strategy.is_public()

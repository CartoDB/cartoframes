from geopandas import GeoDataFrame

from .dataset.registry.base_dataset import BaseDataset
from .dataset.registry.table_dataset import TableDataset
from .dataset.registry.query_dataset import QueryDataset
from .dataset.registry.dataframe_dataset import DataFrameDataset

from ..viz import Map, Layer
from ..auth.defaults import get_default_credentials
from ..utils.utils import is_sql_query, is_table_name

# TODO: This class reuses existing classes from the dataset registry.
# The implementation is temporary and will be refactored when the Dataset is removed.

DOWNLOAD_RETRY_TIMES = 3


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        credentials = kwargs.pop('credentials', None)
        data, args, kwargs = _extract_data_arg(args, kwargs)

        super(CartoDataFrame, self).__init__(*args, **kwargs)

        self._strategy = self._create_strategy(data, schema, credentials)

    @classmethod
    def from_table(cls, table_name, schema=None, credentials=None):
        return cls(table_name, schema=schema, credentials=credentials)

    @classmethod
    def from_query(cls, query, credentials=None):
        return cls(query, credentials=credentials)

    @classmethod
    def from_file(cls, filename, **kwargs):
        gdf = GeoDataFrame.from_file(filename, **kwargs)
        return cls(gdf)

    @classmethod
    def from_features(cls, features, crs=None, columns=None):
        gdf = GeoDataFrame.from_features(features, crs, columns)
        return cls(gdf)

    def download(self, limit=None, decode_geom=None, retry_times=DOWNLOAD_RETRY_TIMES,
                 table_name=None, schema=None, credentials=None):
        self._update_strategy(table_name, schema, credentials)
        df = self._strategy.download(limit, decode_geom, retry_times)
        if df is not None:
            object.__setattr__(self, '_data', df._data)
        return self

    def upload(self, table_name=None, schema=None, with_lnglat=False,
               if_exists=BaseDataset.IF_EXISTS_FAIL, credentials=None):
        self._update_strategy(table_name, schema, credentials)
        self._strategy.upload(if_exists, with_lnglat)
        print('Data uploaded successfully!')

    def plot(self, *args, ** kwargs):
        return Map(Layer(self, *args, **kwargs))

    def delete(self):
        return self._strategy.delete()

    def exists(self):
        return self._strategy.exists()

    def is_public(self):
        return self._strategy.is_public()

    def num_rows(self):
        return self._strategy.get_num_rows()

    def geom_type(self):
        return self._strategy.compute_geom_type()

    def update_info(self, privacy=None, table_name=None):
        return self._strategy.update_dataset_info(privacy, table_name)

    def _create_strategy(self, data, schema, credentials):
        if data is not None:
            if is_sql_query(data):
                return QueryDataset.create(data, credentials)
            elif is_table_name(data):
                return TableDataset.create(data, credentials, schema)
        return DataFrameDataset.create(self, credentials)

    def _update_strategy(self, table_name, schema, credentials):
        if table_name is not None:
            self._strategy.table_name = table_name
        if schema is not None:
            self._strategy.schema = schema
        if credentials is not None:
            self._strategy.credentials = credentials

        if self._strategy.credentials is None:
            # Apply default credentials
            self._strategy.credentials = get_default_credentials()


def _extract_data_arg(args, kwargs):
    data = None

    if len(args):
        data = args[0]

        if isinstance(data, str):
            args = list(args)
            args[0] = None
            args = tuple(args)

    elif 'data' in kwargs:
        data = kwargs['data']

        if isinstance(data, str):
            kwargs['data'] = None

    return data, args, kwargs

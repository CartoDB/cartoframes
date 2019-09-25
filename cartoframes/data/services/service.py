from __future__ import absolute_import

from ...lib import context
from ...auth import get_default_credentials
import uuid
from pandas import DataFrame
from ...data import Dataset


SERVICE_KEYS = ('hires_geocoder', 'isolines')
QUOTA_INFO_KEYS = ('monthly_quota', 'used_quota', 'soft_limit', 'provider')


class Result:
    """
    A Result has two attributes, `data` and `metadata` (a dictionary):

    .. code::

        result = Result(data=..., metadata=...)
        print(result.data)
        print(result.metadata)

    It also is indexable and iterable, the first element being the data:

    .. code::

        data, metadata = Result(data=..., metadata=...)

    And it has a ``select`` method that can be used to retrieve both
    attributes or metadata entries as a tuple, useful to *destructure*
    the data into variables; e.g. to retrieve
    ``result.data`` and ``result.metadata.get('max_value')``:

    .. code::

        data, max_value = result.select('data', 'max_value')


    When retrieving a single element, the ``get`` method can be used,
    which can take a default value argument, just like the dictionary method:

    .. code::

        max_value = result.get(max_value', 0)

    """
    def __init__(self, data=None, metadata=None):
        self.data = data
        self.metadata = metadata

    def __getitem__(self, index):
        # make Result iterable and indexable
        if not isinstance(index, int):
            raise TypeError("Invalid index type {}. It must be an integer".format(type(index).__name__))
        if index < 0 or index > 1:
            raise IndexError("Index out of range: {}. Valid ranges is 0 to 1".format(index))
        if index == 0:
            return self.data
        elif index == 1:
            return self.metadata
        return None

    def select(self, *keys):
        return (self.get(key) for key in keys)

    def get(self, key, default_value=None):
        if hasattr(self, key):
            value = getattr(self, key)
            if value is None:
                value = default_value
        else:
            value = (self.metadata or {}).get(key, default_value)
        return value


class DatasetResult(Result):
    def __init__(self, dataset=None, metadata=None):
        super(DatasetResult, self).__init__(data=dataset, metadata=metadata)

    @property
    def dataset(self):
        return self.data


class DataFrameResult(Result):
    def __init__(self, dataframe=None, metadata=None):
        super(DataFrameResult, self).__init__(data=dataframe, metadata=metadata)

    @property
    def dataframe(self):
        return self.data


class Service(object):

    def __init__(self, credentials=None, quota_service=None):
        self._credentials = credentials or get_default_credentials()
        self._context = context.create_context(self._credentials)
        self._quota_service = quota_service
        if self._quota_service not in SERVICE_KEYS:
            raise ValueError('Invalid service "{}" valid services are: {}'.format(self._quota_service, ', '.join(SERVICE_KEYS)))

    def _quota_info(self, service):
        result = self._execute_query('SELECT * FROM cdb_service_quota_info()')
        for row in result.get('rows'):
            if row.get('service') == service:
                return {k: row.get(k) for k in QUOTA_INFO_KEYS}
        return None

    def used_quota(self):
        info = self._quota_info(self._quota_service)
        return info and info.get('used_quota')

    def available_quota(self):
        info = self._quota_info(self._quota_service)
        return info and (info.get('monthly_quota') - info.get('used_quota'))

    def _new_temporary_table_name(self, base=None):
        return (base or 'table') + '_' + uuid.uuid4().hex[:10]

    def _execute_query(self, query):
        return self._context.execute_query(query)

    def _execute_long_running_query(self, query):
        return self._context.execute_long_running_query(query)

    def _dataset_num_rows(self, dataset):
        # TODO: add count (num_rows) method to Dataset
        if hasattr(dataset, 'dataframe') and dataset.dataframe is not None:
            return len(dataset.dataframe.index)
        elif hasattr(dataset, 'table_name') and dataset.table_name:
            result = self._execute_query("SELECT COUNT(*) FROM {table}".format(table=dataset.table_name))
        else:
            result = self._execute_query("SELECT COUNT(*) FROM ({query}) _query".format(query=dataset.get_query()))
        return result.get('rows')[0].get('count')

    def result(self, data, metadata=None):
        if isinstance(data, DataFrame):
            return DataFrameResult(data, metadata)
        elif isinstance(data, Dataset):
            return DataFrameResult(data, metadata)
        else:
            return Result(data, metadata)

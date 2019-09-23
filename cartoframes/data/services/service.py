from __future__ import absolute_import

from ...lib import context
from ...auth import get_default_credentials
import uuid


SERVICE_KEYS = ('hires_geocoder', 'isolines')
QUOTA_INFO_KEYS = ('monthly_quota', 'used_quota', 'soft_limit', 'provider')


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

import uuid
from collections import namedtuple

from ...io.managers.context_manager import ContextManager

SERVICE_KEYS = ('hires_geocoder', 'isolines')
QUOTA_INFO_KEYS = ('monthly_quota', 'used_quota', 'soft_limit', 'provider')


Result = namedtuple('Result', ['data', 'metadata'])


class Service:

    def __init__(self, credentials=None, quota_service=None):
        self._context_manager = ContextManager(credentials)
        self._credentials = self._context_manager.credentials
        self._quota_service = quota_service
        if self._quota_service not in SERVICE_KEYS:
            raise ValueError('Invalid service "{}" valid services are: {}'.format(
                self._quota_service,
                ', '.join(SERVICE_KEYS)
            ))

    def _quota_info(self, service):
        result = self._execute_query('SELECT * FROM cdb_service_quota_info()')
        for row in result.get('rows'):
            if row.get('service') == service:
                return {k: row.get(k) for k in QUOTA_INFO_KEYS}
        return None

    def provider(self):
        info = self._quota_info(self._quota_service)
        return info and info.get('provider')

    def used_quota(self):
        info = self._quota_info(self._quota_service)
        return info and info.get('used_quota')

    def available_quota(self):
        info = self._quota_info(self._quota_service)
        return info and (info.get('monthly_quota') - info.get('used_quota'))

    def result(self, data, metadata=None):
        return Result(data=data, metadata=metadata)

    def _schema(self):
        return self._context_manager.get_schema()

    def _new_temporary_table_name(self, base=None):
        return (base or 'table') + '_' + uuid.uuid4().hex[:10]

    def _execute_query(self, query):
        return self._context_manager.execute_query(query)

    def _execute_long_running_query(self, query):
        return self._context_manager.execute_long_running_query(query)

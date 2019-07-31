import time
from warnings import warn

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient
from carto.exceptions import CartoRateLimitException

from .base_context import BaseContext
from ..__version__ import __version__

DEFAULT_RETRY_TIMES = 3


class APIContext(BaseContext):
    def __init__(self, credentials):
        self.auth_client = APIKeyAuthClient(
            base_url=credentials.base_url,
            api_key=credentials.api_key,
            session=credentials.session,
            client_id='cartoframes_{}'.format(__version__),
            user_agent='cartoframes_{}'.format(__version__)
        )
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)

    def download(self, query, retry_times=DEFAULT_RETRY_TIMES):
        try:
            return self.copy_client.copyto_stream(query.strip())
        except CartoRateLimitException as err:
            if retry_times > 0:
                retry_times -= 1
                warn('Read call rate limited. Waiting {s} seconds'.format(s=err.retry_after))
                time.sleep(err.retry_after)
                warn('Retrying...')
                return self.download(query.strip(), retry_times=retry_times)
            else:
                warn(('Read call was rate-limited. '
                      'This usually happens when there are multiple queries being read at the same time.'))
                raise err

    def upload(self, query, data):
        return self.copy_client.copyfrom(query.strip(), data)

    def execute_query(self, query, parse_json=True, do_post=True, format=None, **request_args):
        return self.sql_client.send(query.strip(), parse_json, do_post, format, **request_args)

    def execute_long_running_query(self, query):
        return self.batch_sql_client.create_and_wait_for_completion(query.strip())

    def get_schema(self):
        """Get user schema from current credentials"""
        query = 'select current_schema()'
        result = self.execute_query(query, do_post=False)
        return result['rows'][0]['current_schema']

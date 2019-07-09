from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from .client import ClientBase


class APIClient(ClientBase):
    def __init__(self, creds, session, version):
        self.auth_client = APIKeyAuthClient(
            base_url=creds.base_url(),
            api_key=creds.key(),
            session=session,
            client_id='cartoframes_{}'.format(version),
            user_agent='cartoframes_{}'.format(version)
        )
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)

    def download(self):
        pass

    def upload(self):
        pass

    def execute_query(self, query, parse_json=True, do_post=True, format=None, **request_args):
        return self.sql_client.send(query, parse_json, do_post, format, **request_args)



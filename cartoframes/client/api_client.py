from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from client import ClientBase

class APIClient(ClientBase):
    def __init__(self, creds, session):
        self.auth_client = APIKeyAuthClient(
            base_url=creds.base_url(),
            api_key=creds.key(),
            session=session,
            client_id='cartoframes_{}'.format(__version__),
            user_agent='cartoframes_{}'.format(__version__)
        )
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)

    def download(self):
        pass

    def upload(self):
        pass



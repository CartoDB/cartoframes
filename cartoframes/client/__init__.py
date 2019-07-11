from .api_client import APIClient
from .sql_client import SQLClient


def create_client(creds, session=None):
    return APIClient(creds, session)


__all__ = [
    'SQLClient'
]

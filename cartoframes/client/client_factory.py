from .api_client import APIClient


def get_client(creds, session=None):
    return APIClient(creds, session)

from .api_client import APIClient


def create_client(creds, session=None):
    return APIClient(creds, session)

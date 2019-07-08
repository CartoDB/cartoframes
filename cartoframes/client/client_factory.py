from .api_client import APIClient


def get_client(creds, session, version):
    return APIClient(creds, session, version)

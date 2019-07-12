from .api_context import APIContext


def create_context(creds, session=None):
    return APIContext(creds, session)


__all__ = [
]
from .api_context import APIContext


def create_context(credentials, session=None):
    return APIContext(credentials, session)


__all__ = [
]

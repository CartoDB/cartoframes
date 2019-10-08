from __future__ import absolute_import

from .api_context import APIContext


def create_context(credentials):
    return APIContext(credentials)


__all__ = [
]

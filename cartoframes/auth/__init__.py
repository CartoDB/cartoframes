from __future__ import absolute_import

from ..context import CartoContext as Context

default_context = None


def set_default_context(context=None, base_url=None, api_key=None, creds=None, session=None):
    global default_context
    if isinstance(context, Context):
        default_context = context
    elif isinstance(base_url, str) and isinstance(api_key, str):
        _context = Context(base_url, api_key, creds, session)
        default_context = _context
    else:
        raise ValueError('Wrong context data')


__all__ = [
    'Context',
    'set_default_context'
]

from __future__ import absolute_import

from ..credentials import Credentials
from ..context import CartoContext as Context

_default_context = None


def set_default_context(context=None, base_url=None, api_key=None, creds=None, session=None):
    """set_default_context

    From a pair base_url, api_key.

    .. code::

        from cartoframes.auth import set_default_context

        set_default_context(
            base_url='https://your_user_name.carto.com',
            api_key='your api key'
        )

    From context.

    .. code::

        from cartoframes.auth import Context, set_default_context

        context = Context(
            base_url='https://your_user_name.carto.com',
            api_key='your api key'
        )
        set_default_context(context)

    From credentials.

    .. code::

        from cartoframes.auth import Credentials, set_default_context

        creds = Credentials(
            key='abcdefg',
            username='cartoframes'
        )
        set_default_context(creds)
    """
    global _default_context
    if isinstance(context, Context):
        _default_context = context
    elif isinstance(base_url, str) and isinstance(api_key, str):
        _default_context = Context(base_url=base_url, api_key=api_key, session=session)
    elif isinstance(creds, Credentials):
        _default_context = Context(creds=creds, session=session)
    else:
        raise ValueError('Invalid inputs. Pass a Context, a base_url and api_key pair, or a Credentials object.')


__all__ = [
    'Context',
    'set_default_context'
]

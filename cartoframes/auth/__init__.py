"""Auth namespace contains the class to manage authentication: Context.
It also includes the utility method set_default_context."""
from __future__ import absolute_import

from ..credentials import Credentials
from ..context import CartoContext as Context

_default_context = None


def set_default_context(first=None, second=None, base_url=None, api_key=None, context=None, creds=None, session=None):
    """set_default_context

    Args:
        context (:py:class:`Context <cartoframes.auth.Context>`):
          A :py:class:`Context <cartoframes.auth.Context>` instance.
        base_url (str): Base URL of CARTO user account. Cloud-based accounts
          should use the form ``https://{username}.carto.com`` (e.g.,
          https://eschbacher.carto.com for user ``eschbacher``) whether on
          a personal or multi-user account. On-premises installation users
          should ask their admin.
        api_key (str): CARTO API key.
        creds (:py:class:`Credentials <cartoframes.credentials.Credentials>`):
          A :py:class:`Credentials <cartoframes.credentials.Credentials>`
          instance can be used in place of a `base_url`/`api_key` combination.
        session (requests.Session, optional): requests session. See `requests
          documentation
          <http://docs.python-requests.org/en/master/user/advanced/>`__
          for more information.

    Example:

        From a pair base_url, api_key.

        .. code::

            from cartoframes.auth import set_default_context

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

        From a base_url (for public datasets).
        The API key `default_public` is used by default.

        .. code::

            from cartoframes.auth import set_default_context

            set_default_context('https://your_user_name.carto.com')

        From a context.

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

    _context = context if first is None else first
    _base_url = base_url if first is None else first
    _api_key = (api_key if second is None else second) or 'default_public'
    _creds = creds if first is None else first

    if isinstance(_context, Context):
        _default_context = _context
    elif isinstance(_base_url, str) and isinstance(_api_key, str):
        _default_context = Context(base_url=_base_url, api_key=_api_key, session=session)
    elif isinstance(_creds, Credentials):
        _default_context = Context(creds=_creds, session=session)
    else:
        raise ValueError('Invalid inputs. Pass a Context, a base_url and api_key pair, or a Credentials object.')


__all__ = [
    'Context',
    'set_default_context'
]

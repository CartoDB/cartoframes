"""Auth namespace contains the class to manage authentication: Credentials.
It also includes the utility method set_default_credentials."""
from __future__ import absolute_import
import re

from .credentials import Credentials

_default_credentials = None


def set_default_credentials(
        first=None, second=None, credentials=None,
        username=None, base_url=None, api_key=None, session=None):
    """set_default_credentials

    Args:
        credentials (:py:class:`Credentials <cartoframes.credentials.Credentials>`, optional):
          A :py:class:`Credentials <cartoframes.credentials.Credentials>`
          instance can be used in place of a `username | base_url`/`api_key` combination.
        base_url (str, optional): Base URL of CARTO user account. Cloud-based accounts
          should use the form ``https://{username}.carto.com`` (e.g.,
          https://eschbacher.carto.com for user ``eschbacher``) whether on
          a personal or multi-user account. On-premises installation users
          should ask their admin.
        api_key (str, optional): CARTO API key.
        username (str, optional): CARTO user name of the account.
        session (requests.Session, optional): requests session. See `requests
          documentation
          <https://2.python-requests.org/en/master/user/advanced/#session-objects>`__
          for more information.

    Example:

        From a pair username, api_key

        .. code::

            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                username='your_user_name',
                api_key='your api key'
            )

            # or

            set_default_credentials(
                'your_user_name',
                'your api key'
            )

        From a username (for public datasets).
        The API key `default_public` is used by default.

        .. code::

            from cartoframes.auth import set_default_credentials

            set_default_credentials('your_user_name')

        From a pair base_url, api_key.

        .. code::

            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            # or

            set_default_credentials(
                'https://your_user_name.carto.com',
                'your api key'
            )

        From a base_url (for public datasets).
        The API key `default_public` is used by default.

        .. code::

            from cartoframes.auth import set_default_credentials

            set_default_credentials('https://your_user_name.carto.com')

        From a :py:class:`Credentials <cartoframes.auth.Credentials>` class.

        .. code::

            from cartoframes.auth import Credentials, set_default_credentials

            credentials = Credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_credentials(credentials)
    """
    global _default_credentials

    _base_url = base_url if first is None else first
    _username = username if first is None else first
    _api_key = (api_key if second is None else second) or 'default_public'
    _credentials = credentials if first is None else first

    if isinstance(_credentials, Credentials):
        _default_credentials = _credentials

    elif isinstance(_base_url or _username, str) and isinstance(_api_key, str):
        if _base_url and _is_url(_base_url):
            _default_credentials = Credentials(base_url=_base_url, api_key=_api_key)
        else:
            _default_credentials = Credentials(username=_username, api_key=_api_key)

    else:
        raise ValueError(
            'Invalid inputs. Pass a Credentials object, a username and api_key pair or a base_url and api_key pair.')

    if session:
        _default_credentials.session = session


def _is_url(text):
    return re.match(r'^https?://.*$', text)


__all__ = [
    'Credentials',
    'set_default_credentials'
]

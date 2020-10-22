from .credentials import Credentials
from ..utils.utils import is_url, is_json_filepath

_default_credentials = None
_default_do_credentials = None


def set_default_credentials(
        first=None, second=None, credentials=None, filepath=None,
        username=None, base_url=None, api_key=None, session=None, allow_non_secure=False):
    """Set default credentials for all operations that require authentication
    against a CARTO account.

    Args:
        credentials (:py:class:`Credentials <cartoframes.credentials.Credentials>`, optional):
          A :py:class:`Credentials <cartoframes.auth.Credentials>`
          instance can be used in place of a `username | base_url`/`api_key` combination.
        filepath (str, optional): Location where credentials are stored as a JSON file.
        username (str, optional): CARTO user name of the account.
        base_url (str, optional): Base URL of CARTO user account. Cloud-based accounts
          should use the form ``https://{username}.carto.com`` (e.g.,
          https://johnsmith.carto.com for user ``johnsmith``) whether on
          a personal or multi-user account. On-premises installation users
          should ask their admin.
        api_key (str, optional): CARTO API key. Depending on the application,
          this can be a project API key or the account master API key.
        session (requests.Session, optional): requests session. See `requests
          documentation
          <https://2.python-requests.org/en/master/user/advanced/#session-objects>`__
          for more information.
        allow_non_secure (bool, optional): Allow non secure http connections.
            By default is not allowed.

    .. note::

        The recommended way to authenticate in CARTOframes is to read user
        credentials from a JSON file that is structured like this:

        .. code:: JSON

            {
                "username": "your user name",
                "api_key": "your api key",
                "base_url": "https://your_username.carto.com"
            }

        *Note that the ``base_url`` will be different for on premises
        installations.*

        By using the :func:`cartoframes.auth.Credentials.save` method, this
        file will automatically be created for you in a default location
        depending on your operating system. A custom location can also be
        specified as an argument to the method.

        This file can then be read in the following ways:

        >>> set_default_credentials('./carto-project-credentials.json')

    Example:
        Create Credentials from a ``username``, ``api_key`` pair.

        >>> set_default_credentials('johnsmith', 'your api key')

        Create credentials from only a ``username`` (only works with public
        datasets and those marked public with link). If the API key is not
        provided, the public API key `default_public` is used. With this
        setting, only read-only operations can occur (e.g., no publishing of
        maps, reading data from the Data Observatory, or creating new hosted
        datasets).

        >>> set_default_credentials('johnsmith')

        From a pair ``base_url``, ``api_key``.

        >>> set_default_credentials('https://johnsmith.carto.com', 'your api key')

        From a ``base_url`` (for public datasets). The API key `default_public`
        is used by default.

        >>> set_default_credentials('https://johnsmith.carto.com')

        From a :py:class:`Credentials <cartoframes.auth.Credentials>` class.

        >>> credentials = Credentials(
        ...     base_url='https://johnsmith.carto.com',
        ...     api_key='your api key')
        >>> set_default_credentials(credentials)

    """
    global _default_credentials
    _default_credentials = _set_credentials(
        first, second, credentials, filepath, username,
        base_url, api_key, session, allow_non_secure
    )


def get_default_credentials():
    """Retrieve the default credentials if previously set with
    :func:`cartoframes.auth.set_default_credentials` in Python session.

    Example:
        >>> set_default_credentials('creds.json')
        >>> current_creds = get_default_credentials()

    Returns:
        :py:class:`cartoframes.auth.Credentials`: Default credentials
        previously set in current Python session. `None` will be returned if
        default credentials were not previously set.

    """
    return _default_credentials


def unset_default_credentials():
    """Unset the default credentials if previously set with
    :func:`cartoframes.auth.set_default_credentials` in Python session.

    Example:
        >>> set_default_credentials('creds.json')
        >>> unset_default_credentials()

    """
    global _default_credentials
    _default_credentials = None


def set_default_do_credentials(
        first=None, second=None, credentials=None, filepath=None,
        username=None, base_url=None, api_key=None, session=None, allow_non_secure=False):

    global _default_do_credentials
    _default_do_credentials = _set_credentials(
        first, second, credentials, filepath, username,
        base_url, api_key, session, allow_non_secure
    )


def get_default_do_credentials():
    return _default_do_credentials


def unset_default_do_credentials():
    global _default_do_credentials
    _default_do_credentials = None


def _set_credentials(
        first=None, second=None, credentials=None, filepath=None,
        username=None, base_url=None, api_key=None, session=None, allow_non_secure=False):

    _base_url = base_url if first is None else first
    _username = username if first is None else first
    _filepath = filepath if first is None else first
    _api_key = (api_key if second is None else second) or 'default_public'
    _credentials = credentials if first is None else first

    if isinstance(_credentials, Credentials):
        pass

    elif isinstance(_filepath, str) and is_json_filepath(_filepath):
        _credentials = Credentials.from_file(_filepath)

    elif isinstance(_base_url or _username, str) and isinstance(_api_key, str):
        if _base_url and is_url(_base_url):
            _credentials = Credentials(base_url=_base_url, api_key=_api_key, allow_non_secure=allow_non_secure)
        else:
            _credentials = Credentials(username=_username, api_key=_api_key, allow_non_secure=allow_non_secure)

    else:
        _credentials = Credentials.from_file()

    if session:
        _credentials.session = session

    return _credentials

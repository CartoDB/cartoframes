"""Credentials management for cartoframes usage."""
import appdirs
import os
import json
import sys
import warnings
if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

_USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')
_DEFAULT_PATH = os.path.join(_USER_CONFIG_DIR, 'cartocreds.json')


class Credentials(object):
    """Credentials class for managing and storing user CARTO credentials. The
    arguments are listed in order of precedence: :obj:`Credentials` instances
    are first, `key` and `base_url`/`username` are taken next, and
    `config_file` (if given) is taken last. If no arguments are passed, then
    there will be an attempt to retrieve credentials from a previously saved
    session. One of the above scenarios needs to be met to successfully
    instantiate a :obj:`Credentials` object.

    Args:
        api_key (str, optional): API key of user's CARTO account
        username (str, optional): Username of CARTO account
        base_url (str, optional): Base URL used for API calls. This is usually
            of the form `https://eschbacher.carto.com/` for user `eschbacher`.
            On premises installations (and others) have a different URL
            pattern.

    Example:

        .. code::

            from cartoframes.auth import Credentials, Context
            credentials = Credentials(api_key='abcdefg', username='eschbacher')
    """

    def __init__(self, api_key, username=None, base_url=None, session=None):
        if username is None and base_url is None:
            raise ValueError('You must set at least a `username` or a `base_url` parameters')

        self._api_key = api_key
        self._username = username
        self.base_url = base_url or 'https://{}.carto.com/'.format(self._username)
        self._session = session

        self._norm_credentials()

    @classmethod
    def create_from_file(cls, file=None):
        """Retrives credentials from a file. Defaults to the user config directory"""
        with open(config_file or _DEFAULT_PATH, 'r') as f:
            credentials = json.load(f)

        return cls(credentials.get('api_key'), credentials.get('username'))

    @classmethod
    def create_from_credentials(cls, credentials):
        """Retrives credentials from another Credentials object"""
        if isinstance(credentials, Credentials):
            return cls(credentials.api_key, credentials.username, credentials.base_url, credentials.session)

        raise ValueError('`credentials` must a Credentials class instance')

    def __repr__(self):
        return ('Credentials(username={username}, '
                'api_key={key}, '
                'base_url={base_url})').format(username=self._username,
                                               key=self._api_key,
                                               base_url=self._base_url)

    def __eq__(self, obj):
        return self._api_key == obj._api_key and self._username == obj._username and self._base_url == obj._base_url

    @property
    def api_key(self):
        """Credentials api_key"""
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        """Set api_key"""
        self._api_key = api_key

    @property
    def username(self):
        """Credentials username

        Note:
            This does not update the `base_url` attribute. You should use `credentials.base_url = new_abse_url`
        """
        return self._username

    @username.setter
    def username(self, username):
        """Set username"""
        self._username = username

    @property
    def base_url(self):
        """Credentials base_url"""
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        """Set base_url"""
        if urlparse(base_url).scheme != 'https':
            raise ValueError('`base_url`s need to be over `https`. Update your `base_url`.')

        self._base_url = base_url

    @property
    def session(self):
        """Credentials session"""
        return self._session

    @session.setter
    def session(self, session):
        """Set session"""
        self._session = session

    def _norm_credentials(self):
        """Standardize credentials"""
        if self._base_url:
            self._base_url = self._base_url.strip('/')

    def save(self, config_file=None):
        """Saves current user credentials to user directory.

        Args:
            config_loc (str, optional): Location where credentials are to be
                stored. If no argument is provided, it will be send to the
                default location.

        Example:

            .. code::

                from cartoframes import Credentials
                credentials = Credentials(username='eschbacher', api_key='abcdefg')
                credentials.save()  # save to default location

            .. code::

                from cartoframes import Credentials
                credentials = Credentials(username='eschbacher', api_key='abcdefg')
                credentials.save('path/to/credentials/file')
        """

        if config_file is None:
            config_file = _DEFAULT_PATH

            """create directory if not exists"""
            if not os.path.exists(_USER_CONFIG_DIR):
                os.makedirs(_USER_CONFIG_DIR)

        with open(config_file, 'w') as f:
            json.dump({'username': self._username, 'api_key': self._api_key, 'base_url': self._base_url}, f)

    def delete(self, config_file=None):
        """Deletes the credentials file specified in `config_file`. If no
        file is specified, it deletes the default user credential file.

        Args:
            config_file (str): Path to configuration file. Defaults to delete
                the user default location if `None`.

        .. Tip::

            To see if there is a default user credential file stored, do the
            following::

                >>> credentials = Credentials.create_from_file()
                >>> print(credentials)
                Credentials(username=eschbacher, api_key=abcdefg,
                        base_url=https://eschbacher.carto.com/)

        """
        path_to_remove = config_file or _DEFAULT_PATH
        try:
            os.remove(path_to_remove)
            warnings.warn('Credentials at {} successfully removed.'.format(path_to_remove))
        except OSError:
            warnings.warn('No credential file found at {}.'.format(path_to_remove))

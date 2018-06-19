"""Credentials management for cartoframes usage."""
import os
import json
import sys
import warnings
if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
import appdirs

_USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')
_DEFAULT_PATH = os.path.join(_USER_CONFIG_DIR,
                             'cartocreds.json')


class Credentials(object):
    """Credentials class for managing and storing user CARTO credentials. The
    arguments are listed in order of precedence: :obj:`Credentials` instances
    are first, `key` and `base_url`/`username` are taken next, and
    `config_file` (if given) is taken last. If no arguments are passed, then
    there will be an attempt to retrieve credentials from a previously saved
    session. One of the above scenarios needs to be met to successfully
    instantiate a :obj:`Credentials` object.

    Args:
        creds (:obj:`cartoframes.Credentials`, optional): Credentials instance
        key (str, optional): API key of user's CARTO account
        username (str, optional): Username of CARTO account
        base_url (str, optional): Base URL used for API calls. This is usually
            of the form `https://eschbacher.carto.com/` for user `eschbacher`.
            On premises installations (and others) have a different URL
            pattern.
        cred_file (str, optional): Pull credentials from a stored file. If this
            and all other args are not entered, Credentials will attempt to
            load a user config credentials file that was previously set with
            Credentials(...).save().

    Raises:
        RuntimeError: If not enough credential information is passed and no
            stored credentials file is found, this error will be raised.

    Example:

        .. code::

            from cartoframes import Credentials, CartoContext
            creds = Credentials(key='abcdefg', username='eschbacher')
            cc = CartoContext(creds=creds)

    """
    def __init__(self, creds=None, key=None, username=None, base_url=None,
                 cred_file=None):
        self._key = None
        self._username = None
        self._base_url = None
        if creds and isinstance(creds, Credentials):
            self.key(key=creds.key())
            self.username(username=creds.username())
            self.base_url(base_url=creds.base_url())
        elif (key and username) or (key and base_url):
            self.key(key=key)
            self.username(username=username)
            if base_url:
                self.base_url(base_url=base_url)
            else:
                self.base_url(
                    base_url='https://{}.carto.com/'.format(self._username)
                )
        elif cred_file:
            self._retrieve(cred_file)
        else:
            try:
                self._retrieve(_DEFAULT_PATH)
            except:
                raise RuntimeError(
                    'Could not load CARTO credentials. Try setting them with '
                    'the `key` and `username` arguments.'
                )
        self._norm_creds()

    def __repr__(self):
        return ('Credentials(username={username}, '
                'key={key}, '
                'base_url={base_url})').format(username=self._username,
                                               key=self._key,
                                               base_url=self._base_url)

    def _norm_creds(self):
        """Standardize credentials"""
        if self._base_url:
            self._base_url = self._base_url.strip('/')

    def save(self, config_loc=None):
        """Saves current user credentials to user directory.

        Args:
            config_loc (str, optional): Location where credentials are to be
                stored. If no argument is provided, it will be send to the
                default location.

        Example:

            .. code::

                from cartoframes import Credentials
                creds = Credentials(username='eschbacher', key='abcdefg')
                creds.save()  # save to default location

        """
        if not os.path.exists(_USER_CONFIG_DIR):
            """create directory if not exists"""
            os.makedirs(_USER_CONFIG_DIR)
        with open(_DEFAULT_PATH, 'w') as f:
            json.dump({'key': self._key, 'base_url': self._base_url,
                       'username': self._username}, f)

    def _retrieve(self, config_file=None):
        """Retrives credentials from a file. Defaults to the user config
        directory"""
        with open(config_file or _DEFAULT_PATH, 'r') as f:
            creds = json.load(f)
        self._key = creds.get('key')
        self._base_url = creds.get('base_url')
        self._username = creds.get('username')

    def delete(self, config_file=None):
        """Deletes the credentials file specified in `config_file`. If no
        file is specified, it deletes the default user credential file.

        Args:
            config_file (str): Path to configuration file. Defaults to delete
                the user default location if `None`.

        .. Tip::

            To see if there is a default user credential file stored, do the
            following::

                >>> creds = Credentials()
                >>> print(creds)
                Credentials(username=eschbacher, key=abcdefg,
                        base_url=https://eschbacher.carto.com/)

        """
        path_to_remove = config_file or _DEFAULT_PATH
        try:
            os.remove(path_to_remove)
            print('Credentials at {} successfully removed.'.format(
                path_to_remove))
        except OSError as err:
            warnings.warn('No credential file found at {}.'.format(
                path_to_remove))

    def set(self, key=None, username=None, base_url=None):
        """Update the credentials of a Credentials instance instead with new
        values.

        Args:
            key (str): API key of user account. Defaults to previous value if
                not specified.
            username (str): User name of account. This parameter is optional if
                `base_url` is not specified, but defaults to the previous
                value if not set.
            base_url (str): Base URL of user account. This parameter is
                optional if `username` is specified and on CARTO's
                cloud-based account. Generally of the form
                ``https://your_user_name.carto.com/`` for cloud-based accounts.
                If on-prem or otherwise, contact your admin.

        Example:

            .. code::

                from cartoframes import Credentials
                # load credentials saved in previous session
                creds = Credentials()
                # set new API key
                creds.set(key='new_api_key')
                # save new creds to default user config directory
                creds.save()

        Note:
            If the `username` is specified but the `base_url` is not, the
            `base_url` will be updated to ``https://<username>.carto.com/``.
        """
        self.__init__(key=(key or self._key),
                      username=(username or self._username),
                      base_url=base_url)

    def key(self, key=None):
        """Return or set API `key`.

        Args:
            key (str, optional): If set, updates the API key, otherwise returns
                current API key.

        Example:

            .. code::

                >>> from cartoframes import Credentials
                # load credentials saved in previous session
                >>> creds = Credentials()
                # returns current API key
                >>> creds.key()
                'abcdefg'
                # updates API key with new value
                >>> creds.key('new_api_key')
        """
        if key:
            self._key = key
        else:
            return self._key

    def username(self, username=None):
        """Return or set `username`.

        Args:
            username (str, optional): If set, updates the `username`. Otherwise
                returns current `username`.

        Note:
            This does not update the `base_url` attribute. Use
            `Credentials.set` to have that updated with `username`.

        Example:

            .. code::

                >>> from cartoframes import Credentials
                # load credentials saved in previous session
                >>> creds = Credentials()
                # returns current username
                >>> creds.username()
                'eschbacher'
                # updates username with new value
                >>> creds.username('new_username')
        """
        if username:
            self._username = username
        else:
            return self._username

    def base_url(self, base_url=None):
        """Return or set `base_url`.

        Args:
            base_url (str, optional): If set, updates the `base_url`. Otherwise
                returns current `base_url`.

        Note:
            This does not update the `username` attribute. Separately update
            the username with ``Credentials.username`` or update `base_url` and
            `username` at the same time with ``Credentials.set``.

        Example:

            .. code::

                >>> from cartoframes import Credentials
                # load credentials saved in previous session
                >>> creds = Credentials()
                # returns current base_url
                >>> creds.base_url()
                'https://eschbacher.carto.com/'
                # updates base_url with new value
                >>> creds.base_url('new_base_url')
        """
        if base_url:
            # POSTs need to be over HTTPS (e.g., Import API reverts to a GET)
            if urlparse(base_url).scheme != 'https':
                raise ValueError(
		    '`base_url`s need to be over `https`. Update your '
                    '`base_url`.'
		)
            self._base_url = base_url
        else:
            return self._base_url

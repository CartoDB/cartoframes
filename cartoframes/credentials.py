"""API key utility functions
"""
import os
import json
import warnings
import appdirs

_USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')
_DEFAULT_PATH = os.path.join(_USER_CONFIG_DIR,
                             'cartocreds.json')


def create_config_dir():
    """create directory if not exists"""
    if not os.path.exists(_USER_CONFIG_DIR):
        os.makedirs(_USER_CONFIG_DIR)


class Credentials(object):
    """Credentials class for managing and storing user CARTO credentials"""
    def __init__(self, key=None, username=None, base_url=None, cred_file=None):
        if key and username:
            self._key = key
            self._username = username
            if base_url:
                self._base_url = base_url
            else:
                self._base_url = 'https://{}.carto.com/'.format(self._username)
        elif cred_file:
            self.retrieve(cred_file)
        else:
            try:
                creds = json.loads(open(_DEFAULT_PATH).read())
                self._key = creds['key']
                self._base_url = creds['base_url']
            except:
                raise RuntimeError('Could not load CARTO credentials. Try '
                                   'setting them instead.')

    def __repr__(self):
        return ('Credentials(username={username}, '
                'key={key}, '
                'base_url={base_url})').format(username=self._username,
                                               key=self._key,
                                               base_url=self._base_url)

    def save(self):
        """Saves user credentials to user directory"""
        create_config_dir()
        with open(_DEFAULT_PATH, 'w') as f:
            json.dump({'key': self._key, 'base_url': self._base_url}, f)

    def retrieve(self, config_file=None):
        """retrives credentials"""
        with open(config_file or _DEFAULT_PATH, 'r') as f:
            creds = json.load(f)
        self._key = creds.get('key')
        self._base_url = creds.get('base_url')

    def delete(self, config_file=None):
        """Deletes the credentials file

        Args:
            config_file (str): Path to configuration file. Defaults to delete
                the user default location if `None`.
        """
        os.remove(config_file or _DEFAULT_PATH)

    def set(self, key=None, username=None, base_url=None):
        """

        Args:
            creds (dict): Dictionary with keys `username` and/or `key` to set
                new user credentials
            update (bool): Update credentials
        """
        self.__init__(key=(key or self._key),
                      username=(username or self._username),
                      base_url=base_url)

    def key(self, key=None):
        """Return API key if no arguemnt is passed. Updates key to `key`
        if it is passed."""
        if key:
            self._key = key
        else:
            return self._key

    def username(self, username=None):
        """Return username if no argument is passed. Updates username to
        `username` if it is passed.

        Note:
            This does not update the `base_url` attribute.
        """
        if username:
            self._username = username
        else:
            return self._username

    def base_url(self, base_url=None):
        """return base_url"""
        if base_url:
            self._base_url = base_url
        else:
            return self._base_url

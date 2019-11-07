"""Unit tests for cartoframes.keys"""
import os
import pytest

from cartoframes.auth import Credentials
from cartoframes.auth.credentials import _DEFAULT_PATH, _USER_CONFIG_DIR

# FIXME python 2.7 compatibility
try:
    FileNotFoundError
    from io import StringIO
except NameError:
    FileNotFoundError = IOError
    from io import BytesIO as StringIO


class TestCredentials(object):
    def setup_method(self, method):
        self.api_key = 'fake_api_key'
        self.username = 'fake_user'
        self.base_url = 'https://{}.carto.com/'.format(self.username)
        self.onprem_base_url = 'https://turtleland.com/user/{}'.format(self.username)

    def test_credentials_constructor(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials.api_key == self.api_key
        assert credentials.username == self.username
        assert credentials.base_url == self.base_url.strip('/')

    def test_credentials_constructor_without_api_key(self):
        credentials = Credentials(self.username)

        assert credentials.api_key == 'default_public'
        assert credentials.username == self.username
        assert credentials.base_url == self.base_url.strip('/')

    def test_credentials_constructor_props(self):
        credentials = Credentials(api_key=self.api_key, username=self.username)

        assert credentials.api_key == self.api_key
        assert credentials.username == self.username
        assert credentials.base_url == self.base_url.strip('/')

    def test_credentials_baseurl(self):
        credentials = Credentials(api_key=self.api_key, base_url=self.base_url)

        assert credentials.api_key == self.api_key
        assert credentials.username is None
        assert credentials.base_url == self.base_url.strip('/')

    def test_credentials_baseurl_without_https(self):
        with pytest.raises(ValueError):
            Credentials(api_key=self.api_key, base_url=self.base_url.replace('https', 'http'))

    def test_credentials_set_baseurl_without_https(self):
        credentials = Credentials(api_key=self.api_key, base_url=self.base_url)

        with pytest.raises(ValueError):
            credentials.base_url = self.base_url.replace('https', 'http')

    def test_credentials_without_base_url_and_username(self):
        with pytest.raises(ValueError):
            Credentials(api_key=self.api_key)

        with pytest.raises(ValueError):
            Credentials(api_key=self.api_key, username=None, base_url=None)

    def test_credentials_create_from_credentials(self):
        credentials1 = Credentials(api_key='abc123', username='jackson-5')
        credentials2 = Credentials.from_credentials(credentials1)

        assert credentials1.api_key == credentials2.api_key
        assert credentials1.username == credentials2.username
        assert credentials1.base_url == credentials2.base_url

    def test_credentials_create_from_credentials_with_no_credentials(self):
        with pytest.raises(ValueError):
            Credentials.from_credentials({})

    def test_credentials_onprem_baseurl(self):
        credentials = Credentials(api_key=self.api_key, username=self.username, base_url=self.onprem_base_url)

        assert credentials.api_key == self.api_key
        assert credentials.username == self.username
        assert credentials.base_url == self.onprem_base_url.strip('/')

    def test_credentials_api_key_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_api_key = 'new_api_key'
        credentials.api_key = new_api_key

        assert credentials.api_key == new_api_key

    def test_credentials_username_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_username = 'new_username'
        credentials.username = new_username

        assert credentials.username == new_username

    def test_credentials_updating_username_updates_base_url(self):
        base_url = 'https://fakeurl'
        credentials = Credentials(api_key=self.api_key, base_url=base_url)

        assert credentials.base_url == base_url

        new_username = 'new_username'
        expected_url = 'https://{}.carto.com'.format(new_username)
        credentials.username = new_username

        assert credentials.username == new_username
        assert credentials.base_url == expected_url

    def test_credentials_base_url_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_base_url = credentials.base_url + 'new'
        credentials.base_url = new_base_url

        assert credentials.base_url == new_base_url

    def test_credentials_repr(self):
        credentials = Credentials(self.username, self.api_key)

        ans = ("Credentials(username='{username}', "
               "api_key='{api_key}', "
               "base_url='https://{username}.carto.com')").format(username=self.username,
                                                                  api_key=self.api_key)
        assert str(credentials) == ans

    def test_credentials_eq_method(self):
        credentials1 = Credentials(api_key='abc123', username='jackson-5')
        credentials2 = Credentials.from_credentials(credentials1)

        assert credentials1 == credentials2
        credentials2.api_key = 'another_apy_key'
        assert credentials1 != credentials2

    def test_get_api_key_auth_client(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials._api_key_auth_client is None
        credentials.get_api_key_auth_client()
        assert credentials._api_key_auth_client is not None

    def test_get_do_token(self, mocker):
        access_token = '1234'

        class Token:
            def __init__(self):
                self.access_token = access_token

        mocker.patch('carto.do_token.DoTokenManager.get', return_value=Token())

        credentials = Credentials(self.username, self.api_key)
        token = credentials.get_do_token()

        assert token == access_token


class TestCredentialsFromFile(object):
    def setup_method(self, method):
        # remove default credential file
        if os.path.exists(_DEFAULT_PATH):
            os.remove(_DEFAULT_PATH)
        # delete path for user config data
        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)

        self.api_key = 'fake_api_key'
        self.username = 'fake_user'

    def teardown_method(self, method):
        if os.path.exists(_DEFAULT_PATH):
            os.remove(_DEFAULT_PATH)

        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)

    def test_credentials_without_file(self, mocker):
        mocker_stdout = mocker.patch('sys.stdout', new_callable=StringIO)

        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        credentials2 = Credentials.from_file()

        assert credentials1 == credentials2
        assert mocker_stdout.getvalue() == 'User credentials for `{0}` were successfully saved to `{1}`\n'.format(
            self.username, _DEFAULT_PATH)

        credentials1.delete()

        with pytest.raises(FileNotFoundError):
            Credentials.from_file()

    def test_credentials_with_file(self, mocker):
        mocker_stdout = mocker.patch('sys.stdout', new_callable=StringIO)

        file = '/tmp/credentials.json'
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save(file)

        credentials2 = Credentials.from_file(file)

        assert credentials1 == credentials2
        assert mocker_stdout.getvalue() == 'User credentials for `{0}` were successfully saved to `{1}`\n'.format(
            self.username, file)

        credentials1.delete(file)

        with pytest.raises(FileNotFoundError):
            Credentials.from_file(file)

    def test_credentials_with_session(self):
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        session = 'fake_session'
        credentials2 = Credentials.from_file(session=session)

        assert credentials2.session == session

        credentials1.delete()

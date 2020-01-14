"""Unit tests for cartoframes.keys"""
import os
import pytest

from cartoframes.auth import Credentials
from cartoframes.utils.utils import default_config_path
from cartoframes.auth.credentials import DEFAULT_CREDS_FILENAME

DEFAULT_PATH = default_config_path(DEFAULT_CREDS_FILENAME)


class TestCredentials:
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

    def test_credentials_api_key_get(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials.api_key == self.api_key

    def test_credentials_username_get(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials.username == self.username

    def test_credentials_base_url_get(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials.base_url == self.base_url.strip('/')

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

    def test_get_api_key_auth_client(self):
        credentials = Credentials(self.username, self.api_key)

        assert credentials._api_key_auth_client is None
        credentials.get_api_key_auth_client()
        assert credentials._api_key_auth_client is not None

    def test_get_do_credentials(self, mocker):
        access_token = '1234'

        class Token:
            def __init__(self):
                self.access_token = access_token

        mocker.patch('carto.do_token.DoTokenManager.get', return_value=Token())

        credentials = Credentials(self.username, self.api_key)
        do_credentials = credentials.get_do_credentials()

        assert do_credentials.access_token == access_token


class TestCredentialsFromFile:
    def setup_method(self, method):
        # remove default credential file
        if os.path.exists(DEFAULT_PATH):
            os.remove(DEFAULT_PATH)

        self.api_key = 'fake_api_key'
        self.username = 'fake_user'

    def teardown_method(self, method):
        if os.path.exists(DEFAULT_PATH):
            os.remove(DEFAULT_PATH)

    def test_credentials_without_file(self, mocker):
        mocker_log = mocker.patch('cartoframes.utils.logger.log.info')

        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        credentials2 = Credentials.from_file()

        assert credentials1 == credentials2
        mocker_log.assert_called_once_with(
            'User credentials for `{0}` were successfully saved to `{1}`'.format(
                self.username, DEFAULT_PATH))

        credentials1.delete()

        with pytest.raises(FileNotFoundError):
            Credentials.from_file()

    def test_credentials_with_file(self, mocker):
        mocker_log = mocker.patch('cartoframes.utils.logger.log.info')

        filepath = '/tmp/credentials.json'
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save(filepath)

        credentials2 = Credentials.from_file(filepath)

        assert credentials1 == credentials2
        mocker_log.assert_called_once_with(
            'User credentials for `{0}` were successfully saved to `{1}`'.format(
                self.username, filepath))

        credentials1.delete(filepath)

        with pytest.raises(FileNotFoundError):
            Credentials.from_file(filepath)

    def test_credentials_with_session(self):
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        session = 'fake_session'
        credentials2 = Credentials.from_file(session=session)

        assert credentials2.session == session

        credentials1.delete()

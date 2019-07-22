"""Unit tests for cartoframes.keys"""
import unittest
import os
from cartoframes.auth import Credentials
from cartoframes.auth.credentials import _USER_CONFIG_DIR, _DEFAULT_PATH

# FIXME python 2.7 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class TestCredentials(unittest.TestCase):
    def setUp(self):
        self.api_key = 'fake_api_key'
        self.username = 'fake_user'
        self.base_url = 'https://{}.carto.com/'.format(self.username)
        self.onprem_base_url = 'https://turtleland.com/user/{}'.format(self.username)

    def test_credentials_constructor(self):
        credentials = Credentials(self.username, self.api_key)

        self.assertEqual(credentials.api_key, self.api_key)
        self.assertEqual(credentials.username, self.username)
        self.assertEqual(credentials.base_url, self.base_url.strip('/'))

    def test_credentials_constructor_without_api_key(self):
        credentials = Credentials(self.username)

        self.assertEqual(credentials.api_key, 'default_public')
        self.assertEqual(credentials.username, self.username)
        self.assertEqual(credentials.base_url, self.base_url.strip('/'))

    def test_credentials_constructor_props(self):
        credentials = Credentials(api_key=self.api_key, username=self.username)

        self.assertEqual(credentials.api_key, self.api_key)
        self.assertEqual(credentials.username, self.username)
        self.assertEqual(credentials.base_url, self.base_url.strip('/'))

    def test_credentials_baseurl(self):
        credentials = Credentials(api_key=self.api_key, base_url=self.base_url)

        self.assertEqual(credentials.api_key, self.api_key)
        self.assertEqual(credentials.username, None)
        self.assertEqual(credentials.base_url, self.base_url.strip('/'))

    def test_credentials_baseurl_without_https(self):
        with self.assertRaises(ValueError):
            Credentials(api_key=self.api_key, base_url=self.base_url.replace('https', 'http'))

    def test_credentials_set_baseurl_without_https(self):
        credentials = Credentials(api_key=self.api_key, base_url=self.base_url)

        with self.assertRaises(ValueError):
            credentials.base_url = self.base_url.replace('https', 'http')

    def test_credentials_without_base_url_and_username(self):
        with self.assertRaises(ValueError):
            Credentials(api_key=self.api_key)

        with self.assertRaises(ValueError):
            Credentials(api_key=self.api_key, username=None, base_url=None)

    def test_credentials_create_from_credentials(self):
        credentials1 = Credentials(api_key='abc123', username='jackson-5')
        credentials2 = Credentials.from_credentials(credentials1)

        self.assertEqual(credentials1.api_key, credentials2.api_key)
        self.assertEqual(credentials1.username, credentials2.username)
        self.assertEqual(credentials1.base_url, credentials2.base_url)

    def test_credentials_create_from_credentials_with_no_credentials(self):
        with self.assertRaises(ValueError):
            Credentials.from_credentials({})

    def test_credentials_onprem_baseurl(self):
        credentials = Credentials(api_key=self.api_key, username=self.username, base_url=self.onprem_base_url)

        self.assertEqual(credentials.api_key, self.api_key)
        self.assertEqual(credentials.username, self.username)
        self.assertEqual(credentials.base_url, self.onprem_base_url.strip('/'))

    def test_credentials_api_key_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_api_key = 'new_api_key'
        credentials.api_key = new_api_key
        self.assertEqual(credentials.api_key, new_api_key)

    def test_credentials_username_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_username = 'new_username'
        credentials.username = new_username
        self.assertEqual(credentials.username, new_username)

    def test_credentials_updating_username_updates_base_url(self):
        base_url = 'https://fakeurl'
        credentials = Credentials(api_key=self.api_key, base_url=base_url)
        self.assertEqual(credentials.base_url, base_url)

        new_username = 'new_username'
        expected_url = 'https://{}.carto.com'.format(new_username)
        credentials.username = new_username
        self.assertEqual(credentials.username, new_username)
        self.assertEqual(credentials.base_url, expected_url)

    def test_credentials_base_url_get_and_set(self):
        credentials = Credentials(self.username, self.api_key)
        new_base_url = credentials.base_url + 'new'
        credentials.base_url = new_base_url
        self.assertEqual(credentials.base_url, new_base_url)

    def test_credentials_repr(self):
        credentials = Credentials(self.username, self.api_key)

        ans = ("Credentials(username='{username}', "
               "api_key='{api_key}', "
               "base_url='https://{username}.carto.com')").format(username=self.username,
                                                                  api_key=self.api_key)
        self.assertEqual(str(credentials), ans)

    def test_credentials_eq_method(self):
        credentials1 = Credentials(api_key='abc123', username='jackson-5')
        credentials2 = Credentials.from_credentials(credentials1)

        self.assertEqual(credentials1, credentials2)
        credentials2.api_key = 'another_apy_key'
        self.assertNotEqual(credentials1, credentials2)


class TestCredentialsFromFile(unittest.TestCase):
    def setUp(self):
        # remove default credential file
        if os.path.exists(_DEFAULT_PATH):
            os.remove(_DEFAULT_PATH)
        # delete path for user config data
        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)

        self.api_key = 'fake_api_key'
        self.username = 'fake_user'

    def tearDown(self):
        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)

    def test_credentials_without_file(self):
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        credentials2 = Credentials.from_file()
        self.assertEqual(credentials1, credentials2)

        credentials1.delete()

        with self.assertRaises(FileNotFoundError):
            Credentials.from_file()

    def test_credentials_with_file(self):
        file = '/tmp/credentials.json'
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save(file)

        credentials2 = Credentials.from_file(file)
        self.assertEqual(credentials1, credentials2)

        credentials1.delete(file)

        with self.assertRaises(FileNotFoundError):
            Credentials.from_file(file)

    def test_credentials_with_session(self):
        credentials1 = Credentials(self.username, self.api_key)
        credentials1.save()

        session = 'fake_session'
        credentials2 = Credentials.from_file(session=session)
        self.assertEqual(credentials2.session, session)

        credentials1.delete()

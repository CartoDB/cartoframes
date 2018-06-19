"""Unit tests for cartoframes.keys"""
import unittest
import json
import os
import time
from cartoframes import Credentials
from cartoframes.credentials import _USER_CONFIG_DIR, _DEFAULT_PATH


class TestCredentials(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        # remove default credential file
        if os.path.exists(_DEFAULT_PATH):
            os.remove(_DEFAULT_PATH)
        # delete path for user config data
        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)
        self.key = 'seaturtlexyz'
        self.username = 'loggerhead'
        self.base_url = 'https://loggerhead.carto.com/'
        self.onprem_base_url = 'https://turtleland.com/user/{}'.format(
                self.username)
        self.default = {
            'key': 'default_key',
            'username': 'default_username',
            'base_url': 'https://default_username.carto.com/'
        }
        self.default_cred = Credentials(**self.default)
        self.default_cred.save()

    def tearDown(self):
        self.default_cred.delete()
        if os.path.exists(_USER_CONFIG_DIR):
            os.rmdir(_USER_CONFIG_DIR)

    def test_credentials(self):
        """credentials.Credentials common usage"""
        creds = Credentials(key=self.key,
                            username=self.username)

        self.assertEqual(creds.key(), self.key)
        self.assertEqual(creds.username(), self.username)
        self.assertEqual(creds.base_url(), self.base_url.strip('/'))

    def test_credentials_constructor(self):
        """credentials.Credentials object constructor"""
        creds1 = Credentials(key='abc123', username='jackson-5')
        creds2 = Credentials(creds=creds1)

        self.assertEqual(creds1.key(), creds2.key())
        self.assertEqual(creds1.username(), creds2.username())
        self.assertEqual(creds1.base_url(), creds2.base_url())

    def test_credentials_baseurl(self):
        """credentials.Credentials carto.com base_url"""
        creds = Credentials(key=self.key,
                            base_url=self.base_url)

        self.assertEqual(creds.key(), self.key)
        self.assertEqual(creds.username(), None)
        self.assertEqual(creds.base_url(), self.base_url.strip('/'))

        with self.assertRaises(ValueError):
            creds = Credentials(
                key=self.key,
                base_url=self.base_url.replace('https', 'http')
            )

    def test_credentials_onprem_baseurl(self):
        """credentials.Credentials on-prem-style base_url"""
        creds = Credentials(key=self.key,
                            username=self.username,
                            base_url=self.onprem_base_url)

        self.assertEqual(creds.key(), self.key)
        self.assertEqual(creds.username(), self.username)
        self.assertEqual(creds.base_url(), self.onprem_base_url.strip('/'))

    def test_credentials_no_args(self):
        """credentials.Creentials load default cred file"""
        creds = Credentials()

        self.assertEqual(creds.key(), self.default['key'])
        self.assertEqual(creds.username(), self.default['username'])
        self.assertEqual(creds.base_url(), self.default['base_url'].strip('/'))

    def test_credentials_invalid_key(self):
        """credentials.Credentials invalid key"""
        self.default_cred.delete()
        with self.assertRaises(RuntimeError,
                               msg='Did not specify key'):
            Credentials(username=self.username)

    def test_credentials_cred_file(self):
        """credentials.Credentials cred_file"""
        local_cred_file = './test_cred_file_{}.json'.format(
                str(time.time())[-4:])

        # create a credential file with arbitrary name
        with open(local_cred_file, 'w') as f:
            json.dump({'base_url': self.base_url,
                       'key': self.key},
                      f)
        creds = Credentials(cred_file=local_cred_file)
        self.assertEqual(creds.key(), self.key)
        self.assertEqual(creds.base_url(), self.base_url.strip('/'))
        creds.delete(local_cred_file)

    def test_credentials_set(self):
        """credentials.Credentials.set"""
        new_creds = {
                'username': 'andy',
                'key': 'abcdefg'
                }
        self.default_cred.set(**new_creds)

    def test_credentials_key(self):
        """credentials.Credentials.key"""

        creds = Credentials(key='abcdefg', username='andy')
        creds.key('hijklmnop')
        self.assertEqual(creds.key(), 'hijklmnop')

    def test_credentials_retrieve(self):
        """credentials.Credentials.retrieve"""
        local_cred_file = './test_cred_file_{}.json'.format(
                str(time.time())[-4:])

        # create a credential file with arbitrary name
        with open(local_cred_file, 'w') as f:
            json.dump({'base_url': self.base_url,
                       'key': self.key},
                      f)
        self.default_cred._retrieve(local_cred_file)
        self.assertEqual(self.default_cred.key(), self.key)
        self.assertEqual(self.default_cred.username(), None)
        self.assertEqual(self.default_cred.base_url(), self.base_url)

    def test_credentials_delete(self):
        """credentials.Credentials.delete"""

        local_cred_file = './test_cred_file_{}.json'.format(
                str(time.time())[-4:])

        # create a credentials file
        with open(local_cred_file, 'w') as f:
            json.dump({'base_url': self.base_url,
                       'key': self.key},
                      f)

        # check if it's there
        self.assertTrue(os.path.isfile(local_cred_file))

        # load credentials file
        creds = Credentials(cred_file=local_cred_file)

        # delete credentials file
        creds.delete(local_cred_file)

        # ensure it's deleted
        self.assertTrue(not os.path.isfile(local_cred_file))

        self.assertIsNone(creds.delete('non_existent_file'))

    def test_credentials_username(self):
        """credentials.Credentials.username"""
        self.default_cred.username('updated_username')
        self.assertEqual(self.default_cred.username(),
                         'updated_username')

    def test_credentials_base_url(self):
        """credentials.Credentials.base_url"""
        new_base_url = 'https://updated_username.carto.com/'
        self.default_cred.base_url(new_base_url)
        self.assertEqual(self.default_cred.base_url(),
                         new_base_url)

    def test_credentials_repr(self):
        """credentials.Credentials.__repr__"""
        ans = ('Credentials(username=default_username, '
               'key=default_key, '
               'base_url=https://default_username.carto.com)')
        self.assertEqual(str(self.default_cred), ans)

"""Unit tests for cartoframes.keys"""
import unittest
from cartoframes import credentials, context

class TestKeyStore(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        self.key = 'thisisakey'
        self.base_url = 'https://test.carto.com'

    def test_key_null(self):
        """Test case where API key does not exist"""
        credentials._remove_creds()
        with self.assertRaises(EnvironmentError):
            context.CartoContext()
        credentials.set_credentials()
        with self.assertRaises(ValueError):
            context.CartoContext(base_url=self.base_url)
        with self.assertRaises(ValueError):
            context.CartoContext(api_key=self.key)
        with self.assertRaises(ValueError):
            context.CartoContext()

    def test_key_setting(self):
        """Test case where API key is valid"""
        credentials._remove_creds()
        credentials.set_api_key(self.key)
        context.CartoContext(base_url=self.base_url)
        with self.assertRaises(TypeError):
            credentials.set_api_key(self.key, overwrite=False)
        credentials.set_api_key(self.key[::-1], overwrite=True)
        self.assertEqual(credentials.api_key(), self.key[::-1])


    def test_base_url_setting(self):
        """Test case where API base url is valid"""
        credentials._remove_creds()
        credentials.set_base_url(self.base_url)
        context.CartoContext(api_key=self.key)
        with self.assertRaises(TypeError):
            credentials.set_base_url(self.base_url, overwrite=False)
        credentials.set_base_url(self.base_url[::-1], overwrite=True)
        self.assertEqual(credentials.base_url(), self.base_url[::-1])

    def test_set_credentials(self):
        """Test case where API url is valid"""
        credentials._remove_creds()
        credentials.set_credentials(base_url=self.base_url, api_key=self.key)
        context.CartoContext()
        with self.assertRaises(TypeError):
            credentials.set_credentials(base_url=self.base_url[::-1],
                                        api_key=self.key[::-1], overwrite=False)
        credentials.set_credentials(base_url=self.base_url[::-1],
                                    api_key=self.key[::-1], overwrite=True)
        self.assertEqual(credentials.credentials(),
                         dict(api_key=self.key[::-1],
                              base_url=self.base_url[::-1]))

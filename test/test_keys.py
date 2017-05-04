"""Unit tests for cartoframes.keys"""
import unittest
from cartoframes import keys, context

class TestKeyStore(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        self.key = 'thisisakey'
        self.url = 'https://test.carto.com'

    def test_key_null(self):
        """Test case where API key does not exist"""
        keys._remove_creds()
        with self.assertRaises(EnvironmentError):
            context.CartoContext()
        keys.set_credentials()
        with self.assertRaises(ValueError):
            context.CartoContext(base_url=self.url)
        with self.assertRaises(ValueError):
            context.CartoContext(api_key=self.key)
        with self.assertRaises(ValueError):
            context.CartoContext()

    def test_key_setting(self):
        """Test case where API key is valid"""
        keys._remove_creds()
        keys.set_api_key(self.key)
        context.CartoContext(base_url=self.url)
        with self.assertRaises(TypeError):
            keys.set_api_key(self.key, overwrite=False)
        keys.set_api_key(self.key[::-1], overwrite=True)
        self.assertEquals(keys.api_key(), self.key[::-1])


    def test_url_setting(self):
        """Test case where API url is valid"""
        keys._remove_creds()
        keys.set_url(self.url)
        context.CartoContext(api_key=self.key)
        with self.assertRaises(TypeError):
            keys.set_url(self.url, overwrite=False)
        keys.set_url(self.url[::-1], overwrite=True)
        self.assertEquals(keys.url(), self.url[::-1])

    def test_set_credentials(self):
        """Test case where API url is valid"""
        keys._remove_creds()
        keys.set_credentials(url=self.url, api_key=self.key)
        context.CartoContext()
        with self.assertRaises(TypeError):
            keys.set_credentials(url=self.url[::-1], api_key=self.key[::-1], overwrite=False)
        keys.set_credentials(url=self.url[::-1], api_key=self.key[::-1], overwrite=True)
        self.assertEquals(keys.credentials(),
                          dict(api_key=self.key[::-1], 
                               url=self.url[::-1]))

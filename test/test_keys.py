"""Unit tests for cartoframes.keys"""
import unittest
from cartoframes import keys, context

class TestKeyStore(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        self.key = 'thisisakey'
        self.base_url = 'https://test.carto.com'

    def test_key_null(self):
        """Test case where API key does not exist"""
        keys._remove_creds()
        with self.assertRaises(EnvironmentError):
            context.CartoContext()
        keys.set_credentials()
        with self.assertRaises(ValueError):
            context.CartoContext(base_url=self.base_url)
        with self.assertRaises(ValueError):
            context.CartoContext(api_key=self.key)
        with self.assertRaises(ValueError):
            context.CartoContext()

    def test_key_setting(self):
        """Test case where API key is valid"""
        keys._remove_creds()
        keys.set_api_key(self.key)
        context.CartoContext(base_url=self.base_url)
        with self.assertRaises(TypeError):
            keys.set_api_key(self.key, overwrite=False)
        keys.set_api_key(self.key[::-1], overwrite=True)
        self.assertEquals(keys.api_key(), self.key[::-1])


    def test_base_url_setting(self):
        """Test case where API base url is valid"""
        keys._remove_creds()
        keys.set_base_url(self.base_url)
        context.CartoContext(api_key=self.key)
        with self.assertRaises(TypeError):
            keys.set_base_url(self.base_url, overwrite=False)
        keys.set_base_url(self.base_url[::-1], overwrite=True)
        self.assertEquals(keys.base_url(), self.base_url[::-1])

    def test_set_credentials(self):
        """Test case where API url is valid"""
        keys._remove_creds()
        keys.set_credentials(base_url=self.base_url, api_key=self.key)
        context.CartoContext()
        with self.assertRaises(TypeError):
            keys.set_credentials(base_url=self.base_url[::-1], api_key=self.key[::-1], overwrite=False)
        keys.set_credentials(base_url=self.base_url[::-1], api_key=self.key[::-1], overwrite=True)
        self.assertEquals(keys.credentials(),
                          dict(api_key=self.key[::-1],
                               base_url=self.base_url[::-1]))

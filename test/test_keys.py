"""Unit tests for cartoframes.keys"""
import unittest
from cartoframes import keys, context

class TestKeyStore(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        self.good_key = 'thisisakey'

    def test_key_null(self):
        """Test case where API key does not exist"""
        keys._clear_key()
        with self.assertRaises(ValueError):
            context.CartoContext('https://test.carto.com', keys.api_key())

    def test_key_setting(self):
        """Test case where API key is valid"""
        keys.set_key(self.good_key)
        context.CartoContext('https://test.carto.com')

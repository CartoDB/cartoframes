from unittest import TestCase
from .. import keys, context
import os
import shutil as sh

class TestKeyStore(TestCase):
    def setUp(self):
        self.good_key = 'thisisakey'

    def test_key_null(self):
        keys._clear_sitekey()
        with self.assertRaises(ValueError):
            context.CartoContext('https://test.carto.com', keys.APIKEY())

    def test_key_setting(self):
        keys.set_sitekey(self.good_key)
        context.CartoContext('https://test.carto.com')

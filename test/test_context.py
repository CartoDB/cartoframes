"""Unit tests for cartoframes.layers"""
import unittest
import os
import cartoframes
from carto.exceptions import CartoException


class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    self.apikey = os.environ["APIKEY"]
    self.username = os.environ["USERNAME"]
    self.baseurl = 'https://{username}.carto.com/'.format(username=USERNAME)
    self.valid_columns = set(['the_geom', 'the_geom_webmercator', 'lsad10',
                              'name10', 'geoid10', 'affgeoid10', 'pumace10',
                              'statefp10', 'awater10', 'aland10','updated_at',
                              'created_at'])

    def test_cartocontext_read(self):
        """cartoframes.CartoContext.read basic usage"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        # fails on non-existent table
        with self.assertRaises(CartoException):
            df = cc.read('non_existent_table')
        # normal table
        df = cc.read('cb_2013_puma10_500k')
        self.assertTrue(set(df.columns) == self.valid_columns)
        self.assertTrue(len(df) == 2379)


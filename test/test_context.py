"""Unit tests for cartoframes.layers"""
import unittest
import os
import json
import cartoframes
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient

class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    def setUp(self):
        creds = json.loads(open('test/secret.json').read())
        self.apikey = os.environ.get('APIKEY', creds['APIKEY'])
        self.username = os.environ.get('USERNAME', creds['USERNAME'])
        self.baseurl = 'https://{username}.carto.com/'.format(username=self.username)
        self.valid_columns = set(['the_geom', 'the_geom_webmercator', 'lsad10',
                                  'name10', 'geoid10', 'affgeoid10', 'pumace10',
                                  'statefp10', 'awater10', 'aland10','updated_at',
                                  'created_at'])
        self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                            api_key=self.apikey)
        self.sql_client = SQLClient(self.auth_client)

    def test_cartocontext(self):
        """cartoframes.CartoContext properties"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertTrue(cc.api_key == self.apikey)
        self.assertTrue(cc.base_url == self.baseurl)
        self.assertTrue(cc.username == self.username)
        self.assertTrue(not cc.is_org)
        # TODO: how to test instances of a class?
        # self.assertTrue(cc.auth_client.__dict__ == self.auth_client.__dict__)
        # self.assertTrue(cc.sql_client.__dict__ == self.sql_client.__dict__)

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


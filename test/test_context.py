"""Unit tests for cartoframes.layers"""
import unittest
import os
import sys
import json
import random
import cartoframes
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
import pandas as pd

class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    def setUp(self):
        if (os.environ.get('APIKEY') is None or
            os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
            except OSError:
                print("Create a `secret.json` file by renaming "
                      "`secret.json.sample` to `secret.json` and updating "
                      "the credentials to match your environment.")
                raise
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
        self.baseurl = 'https://{username}.carto.com/'.format(username=self.username)
        self.valid_columns = set(['the_geom', 'the_geom_webmercator', 'lsad10',
                                  'name10', 'geoid10', 'affgeoid10', 'pumace10',
                                  'statefp10', 'awater10', 'aland10','updated_at',
                                  'created_at'])
        self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                            api_key=self.apikey)
        self.sql_client = SQLClient(self.auth_client)
        self.test_read_table = 'cb_2013_puma10_500k'
        self.test_write_table = 'cartoframes_test_table_{ver}'.format(
            ver=sys.version[0:3].replace('.', '_'))

    def tearDown(self):
        """restore to original state"""
        self.sql_client.send('''
            DROP TABLE IF EXISTS "{}"
            '''.format(self.test_write_table))

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

    def test_cartocontext_isorguser(self):
        """cartoframes.CartoContext._is_org_user"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                              api_key=self.apikey)
        self.assertTrue(not cc._is_org_user())

    def test_cartocontext_read(self):
        """cartoframes.CartoContext.read basic usage"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        # fails if limit is smaller than zero
        with self.assertRaises(ValueError):
            df = cc.read('sea_horses', limit=-10)
        # fails if not an int
        with self.assertRaises(ValueError):
            df = cc.read('sea_horses', limit=3.14159)
        with self.assertRaises(ValueError):
            df = cc.read('sea_horses', limit='acadia')

        # fails on non-existent table
        with self.assertRaises(CartoException):
            df = cc.read('non_existent_table')

        # normal table
        df = cc.read(self.test_read_table)
        self.assertTrue(set(df.columns) == self.valid_columns)
        self.assertTrue(len(df) == 2379)


    def test_cartocontext_write(self):
        """cartoframes.CartoContext.write"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        data = {'nums': list(range(100, 0, -1)),
                'category': [random.choice('abcdefghijklmnop')
                             for _ in range(100)],
                'lat': [0.01 * i for i in range(100)],
                'long': [-0.01 * i for i in range(100)]}
        schema = {'nums': int,
                  'category': 'object',
                  'lat': float,
                  'long': float}
        df = pd.DataFrame(data).astype(schema)
        cc.write(df, self.test_write_table)

        # check if table exists
        resp = self.sql_client.send('''
            SELECT *
            FROM {table}
            LIMIT 0
            '''.format(table=self.test_write_table))
        self.assertTrue(resp is not None)

        # check that table has same number of rows
        resp = self.sql_client.send('''
            SELECT count(*)
            FROM {table}'''.format(table=self.test_write_table))
        self.assertEqual(resp['rows'][0]['count'], len(df))

        # should error for existing table
        with self.assertRaises(NameError):
            cc.write(df, self.test_read_table, overwrite=False)

        # overwrite table and create the_geom column
        cc.write(df, self.test_write_table,
                 overwrite=True,
                 lnglat=('long', 'lat'))

        resp = self.sql_client.send('''
            SELECT count(*) AS num_rows, count(the_geom) AS num_geoms
            FROM {table}
            '''.format(table=self.test_write_table))
        # number of geoms should equal number of rows
        self.assertEqual(resp['rows'][0]['num_rows'],
                         resp['rows'][0]['num_geoms'])

# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.services.Geocode"""
import unittest
import os
import sys
import json
import warnings
import pandas as pd
import logging

from carto.exceptions import CartoException

from cartoframes.data import Dataset
from cartoframes.auth import Credentials
from cartoframes.utils.columns import normalize_name


from cartoframes.data.clients import SQLClient


from cartoframes.data.services import Isolines


try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

from test.helpers import _UserUrlLoader, _ReportQuotas

warnings.filterwarnings('ignore')


class TestIsochrones(unittest.TestCase, _UserUrlLoader, _ReportQuotas):
    """Tests for cartoframes.data.service.Geocode"""

    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except:  # noqa: E722
                warnings.warn("Skipping Context tests. To test it, "
                              "create a `secret.json` file in test/ by "
                              "renaming `secret.json.sample` to `secret.json` "
                              "and updating the credentials to match your "
                              "environment.")
                self.apikey = None
                self.username = None
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        # sets skip value
        self.no_credentials = self.apikey is None or self.username is None

        # table naming info
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        has_gpd = 'gpd' if os.environ.get('USE_GEOPANDAS') else 'nongpd'
        pyver = sys.version[0:3].replace('.', '_')
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER') or 'none'

        # Skip tests checking quotas when running in TRAVIS
        # since usually multiple tests will be running concurrently
        # in that case
        self.no_credits = self.no_credentials or buildnum != 'none'

        self.test_slug = '{ver}_{num}_{mpl}_{gpd}'.format(
            ver=pyver, num=buildnum, mpl=has_mpl, gpd=has_gpd
        )

        self.test_tables = []

        self.base_url = self.user_url().format(username=self.username)
        self.credentials = Credentials(self.username, self.apikey, self.base_url)
        self.sql_client = SQLClient(self.credentials)

        # self.points = [
        #     ['a',-73.99239,40.74497],
        #     ['b',-3.70399,40.42012],
        #     ['c',-5.98312,37.35547]
        # ]

        self.points = [
            ['a','0101000020E610000028B85851837F52C025404D2D5B5F4440'],
            ['b','0101000020E610000036B05582C5A10DC0A032FE7DC6354440'],
            ['c','0101000020E6100000912C6002B7EE17C0C45A7C0A80AD4240']
        ]
        self.tearDown()

    def skip(self, if_no_credits=False, if_no_credentials=False):
        if self.no_credits and if_no_credits:
            raise unittest.SkipTest("skipping this test to avoid consuming credits")
        if self.no_credentials and if_no_credentials:
            raise unittest.SkipTest("no carto credentials, skipping this test")

    def get_test_table_name(self, name):
        n = len(self.test_tables) + 1
        table_name = normalize_name(
            'cf_test_table_{name}_{n}_{slug}'.format(name=name, n=n, slug=self.test_slug)
        )
        self.test_tables.append(table_name)
        return table_name

    def tearDown(self):
        """restore to original state"""
        sql_drop = 'DROP TABLE IF EXISTS {};'

        for table in self.test_tables:
            try:
                Dataset(table, credentials=self.credentials).delete()
                self.sql_client.query(sql_drop.format(table))
            except CartoException:
                warnings.warn('Error deleting tables')

    # service: isolines, hires_geocoder
    def used_quota(self, iso):
        return TestIsochrones.update_quotas('isolines', iso.used_quota())

    def test_isolines_from_dataframe_dataset(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        ds = Dataset(df)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrone_areas(ds, [100,1000], mode='car', dry_run=True)
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrone_areas(ds, [100,1000], mode='car').data
        self.assertTrue(isinstance(result, Dataset))
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)

    def test_isolines_from_dataframe_dataset_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        ds = Dataset(df)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrone_areas(ds, [100,1000], mode='car', dry_run=True)
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrone_areas(ds, [100,1000], mode='car').data
        self.assertTrue(isinstance(result, Dataset))
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)

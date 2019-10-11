# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.services.Isolines"""
import unittest
import os
import sys
import json
import warnings
import pandas as pd

from carto.exceptions import CartoException

from cartoframes.data import Dataset
from cartoframes.auth import Credentials
from cartoframes.utils.columns import normalize_name


from cartoframes.data.clients import SQLClient


from cartoframes.data.services import Isolines


from test.helpers import _UserUrlLoader, _ReportQuotas


warnings.filterwarnings('ignore')


class TestIsolines(unittest.TestCase, _UserUrlLoader, _ReportQuotas):
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
        pyver = sys.version[0:3].replace('.', '_')
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER') or 'none'

        # Skip tests checking quotas when running in TRAVIS
        # since usually multiple tests will be running concurrently
        # in that case
        self.no_credits = self.no_credentials or buildnum != 'none'

        self.test_slug = '{ver}_{num}_{mpl}'.format(
            ver=pyver, num=buildnum, mpl=has_mpl
        )

        self.test_tables = []

        self.base_url = self.user_url().format(username=self.username)
        self.credentials = Credentials(self.username, self.apikey, self.base_url)
        self.sql_client = SQLClient(self.credentials)

        self.points = [
            ['a', '0101000020E610000028B85851837F52C025404D2D5B5F4440'],
            ['b', '0101000020E610000036B05582C5A10DC0A032FE7DC6354440'],
            ['c', '0101000020E6100000912C6002B7EE17C0C45A7C0A80AD4240']
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

    def used_quota(self, iso):
        return TestIsolines.update_quotas('isolines', iso.used_quota())

    def points_query(self):
        point_query = "SELECT '{name}' AS name, '{geom}'::geometry AS the_geom"
        return ' UNION '.join([point_query.format(name=name, geom=geom) for name, geom in self.points])

    def test_isochrones_from_dataframe_dataset(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        ds = Dataset(df, credentials=self.credentials)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result, meta = iso.isochrones(ds, [100, 1000], mode='car')
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_local())
        self.assertEqual(meta.get('required_quota'), 6)
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('cartodb_id' in result.dataframe)
        self.assertTrue('source_id' in result_columns)
        self.assertTrue('source_id' in result.dataframe)
        self.assertEqual(result.dataframe['source_id'].min(), df.index.min())
        self.assertEqual(result.dataframe['source_id'].max(), df.index.max())

    def test_isochrones_from_dataframe_dataset_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        ds = Dataset(df, credentials=self.credentials)

        quota = self.used_quota(iso)

        table_name = self.get_test_table_name('isodf')

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=table_name, dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=table_name).data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_remote())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('source_id' in result_columns)

    def test_isochrones_from_dataframe(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(df, [100, 1000], mode='car', dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(df, [100, 1000], mode='car').data
        self.assertTrue(isinstance(result, pd.DataFrame))
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        self.assertTrue('the_geom' in result)
        self.assertTrue('data_range' in result)
        self.assertEqual(len(result.index), 6)
        result_columns = Dataset(result).get_column_names()
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('source_id' in result_columns)
        self.assertEqual(result['source_id'].min(), df.index.min())
        self.assertEqual(result['source_id'].max(), df.index.max())

    def test_isochrones_from_dataframe_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])

        quota = self.used_quota(iso)

        table_name = self.get_test_table_name('isodfds')

        # Preview
        result = iso.isochrones(df, [100, 1000], mode='car', table_name=table_name, dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(df, [100, 1000], mode='car', table_name=table_name) .data
        self.assertTrue(isinstance(result, pd.DataFrame))
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        self.assertTrue('the_geom' in result)
        self.assertTrue('data_range' in result)
        self.assertEqual(len(result.index), 6)

        ds = Dataset(table_name, credentials=self.credentials)
        result_columns = ds.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(ds.get_num_rows(), 6)
        self.assertTrue('source_id' in result_columns)

    def test_isochrones_from_table_dataset(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        table_name = self.get_test_table_name('isotb')
        Dataset(df).upload(table_name=table_name, credentials=self.credentials)
        ds = Dataset(table_name, credentials=self.credentials)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car').data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_local())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('cartodb_id' in result.dataframe)
        self.assertTrue('source_id' in result_columns)
        self.assertTrue('source_id' in result.dataframe)

    def test_isochrones_from_table_dataset_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        table_name = self.get_test_table_name('isotb')
        Dataset(df).upload(table_name=table_name, credentials=self.credentials)
        ds = Dataset(table_name, credentials=self.credentials)

        result_table_name = self.get_test_table_name('isotbr')

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=result_table_name, dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=result_table_name).data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_remote())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('source_id' in result_columns)

    def test_isochrones_from_query_dataset(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        ds = Dataset(self.points_query(), credentials=self.credentials)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car').data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_local())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('cartodb_id' in result.dataframe)
        self.assertFalse('source_id' in result_columns)
        self.assertFalse('source_id' in result.dataframe)

    def test_isochrones_from_table_query_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        ds = Dataset(self.points_query(), credentials=self.credentials)

        result_table_name = self.get_test_table_name('isotbr')

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=result_table_name, dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car', table_name=result_table_name).data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_remote())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertFalse('source_id' in result_columns)

    def test_isodistances_from_dataframe(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])

        quota = self.used_quota(iso)

        # Preview
        result = iso.isodistances(df, [100, 1000], mode='car', dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isodistances
        result = iso.isodistances(df, [100, 1000], mode='car').data
        self.assertTrue(isinstance(result, pd.DataFrame))
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        self.assertTrue('the_geom' in result)
        self.assertTrue('data_range' in result)
        self.assertEqual(len(result.index), 6)

    def test_isochrones_from_dataframe_dataset_with_isoline_options(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        iso = Isolines(credentials=self.credentials)

        df = pd.DataFrame(self.points, columns=['name', 'the_geom'])
        ds = Dataset(df, credentials=self.credentials)

        quota = self.used_quota(iso)

        # Preview
        result = iso.isochrones(ds, [100, 1000], mode='car', maxpoints=10, dry_run=True).metadata
        self.assertEqual(result.get('required_quota'), 6)
        self.assertEqual(self.used_quota(iso), quota)

        # Isochrones
        result = iso.isochrones(ds, [100, 1000], mode='car', maxpoints=10).data
        self.assertTrue(isinstance(result, Dataset))
        self.assertTrue(result.is_local())
        quota += 6
        self.assertEqual(self.used_quota(iso), quota)
        result_columns = result.get_column_names()
        self.assertTrue('the_geom' in result_columns)
        self.assertTrue('data_range' in result_columns)
        self.assertEqual(result.get_num_rows(), 6)
        self.assertTrue('cartodb_id' in result_columns)
        self.assertTrue('cartodb_id' in result.dataframe)
        self.assertTrue('source_id' in result_columns)
        self.assertTrue('source_id' in result.dataframe)

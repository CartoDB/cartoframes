# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.services.Geocode"""
import unittest
import os
import sys
import json
import warnings
import pandas as pd
import geopandas as gpd

from carto.exceptions import CartoException

from cartoframes.data import Dataset
from cartoframes.auth import Credentials
from cartoframes.data.clients import SQLClient
from cartoframes.data.services import Geocoding
from cartoframes.utils.columns import normalize_name
from cartoframes.utils.geom_utils import RESERVED_GEO_COLUMN_NAME

from ...helpers import _UserUrlLoader, _ReportQuotas

warnings.filterwarnings('ignore')


class TestGeocoding(unittest.TestCase, _UserUrlLoader, _ReportQuotas):
    """Tests for cartoframes.data.service.Geocoding"""

    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('tests/e2e/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except Exception:  # noqa: E722
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

    def used_quota(self, gc):
        return TestGeocoding.update_quotas('geocode', gc.used_quota())

    def test_invalid_arguments(self):
        gc = Geocoding(credentials=self.credentials)
        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city={'columna': 'city'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', state={'columna': 'city'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', country={'columna': 'city'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city={'column': 'ciudad'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', state={'column': 'ciudad'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', country={'column': 'ciudad'})
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city='ciudad')
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', state='ciudad')
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', country='ciudad')
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city="'city'")
        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city={'column': 'city', 'value': 'London'})

    def test_geocode_dataframe(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        self.assertTrue('cartodb_id' in gc_df)
        self.assertEqual(gc_df.index.name, 'cartodb_id')

        # Preview, Geocode again (should do nothing)
        info = gc.geocode(gc_df, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)
        info = gc.geocode(gc_df, street='address', city='city', country={'value': 'Spain'}).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)

        # Incremental geocoding: modify one row
        gc_df.at[1, 'address'] = 'Gran Via 48'
        info = gc.geocode(gc_df, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(self.used_quota(gc), quota)
        info = gc.geocode(gc_df, street='address', city={'column': 'city'}, country={'value': 'Spain'}).metadata
        self.assertEqual(info.get('required_quota'), 1)
        quota += 1
        self.assertEqual(self.used_quota(gc), quota)

    def test_geocode_dataframe_preserves_input_cartodb(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame(
            [[1, 'Gran Via 46', 'Madrid'], [2, 'Ebro 1', 'Sevilla']], columns=['cartodb_id', 'address', 'city'])

        quota = self.used_quota(gc)

        gc_df = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}).data
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertTrue('cartodb_id' in gc_df)

    def test_geocode_dataframe_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        table_name = self.get_test_table_name('gcdf')

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          table_name=table_name, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, table_name=table_name)
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        # This could change with provider:
        # self.assertEqual(gc_df.the_geom[1], '0101000020E61000002F34D769A4A50DC0C425C79DD2354440')
        # self.assertEqual(gc_df.the_geom[2], '0101000020E6100000912C6002B7EE17C0C45A7C0A80AD4240')
        self.assertIsNotNone(gc_df.the_geom)
        dataset = Dataset(table_name, credentials=self.credentials)
        dl_df = dataset.download()
        self.assertIsNotNone(dl_df.the_geom)
        self.assertTrue(dl_df.equals(gc_df.drop(RESERVED_GEO_COLUMN_NAME, 1)))
        self.assertTrue('cartodb_id' in dataset.get_column_names())
        self.assertEqual(dl_df.index.name, 'cartodb_id')

    def test_geocode_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])
        table_name = self.get_test_table_name('gctb')
        Dataset(df).upload(table_name=table_name, credentials=self.credentials)
        ds = Dataset(table_name, credentials=self.credentials)

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertEqual(gc_ds.table_name, table_name)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())

        # Preview, Geocode again (should do nothing)
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)

        # Incremental geocoding: modify one row
        self.sql_client.query("UPDATE {table} SET address='Gran Via 48' WHERE cartodb_id=1".format(table=table_name))
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(self.used_quota(gc), quota)
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}).metadata
        self.assertEqual(info.get('required_quota'), 1)
        quota += 1
        self.assertEqual(self.used_quota(gc), quota)

    def test_geocode_table_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])
        table_name = self.get_test_table_name('gctb')
        Dataset(df).upload(table_name=table_name, credentials=self.credentials)
        ds = Dataset(table_name, credentials=self.credentials)

        new_table_name = self.get_test_table_name('gctb')

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'},
                          table_name=new_table_name, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'},
                                 table_name=new_table_name)
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertEqual(gc_ds.table_name, new_table_name)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())

        # Original table should not have been geocoded
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Preview, Geocode again (should do nothing)
        info = gc.geocode(gc_ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)
        info = gc.geocode(gc_ds, street='address', city='city', country={'value': 'Spain'}).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)

    def test_geocode_dataframe_dataset(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])
        ds = Dataset(df)

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_ds.dataframe.the_geom)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())
        self.assertTrue('cartodb_id' in gc_ds.dataframe)
        self.assertEqual(gc_ds.dataframe.index.name, 'cartodb_id')

    def test_geocode_dataframe_dataset_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])
        ds = Dataset(df)

        quota = self.used_quota(gc)

        table_name = self.get_test_table_name('gcdfds')

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'},
                          table_name=table_name, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, table_name=table_name)
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())

    def test_geocode_query(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        ds = Dataset("SELECT 'Gran Via 46' AS address, 'Madrid' AS city", credentials=self.credentials)

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(info.get('successfully_geocoded'), 1)
        self.assertEqual(info.get('final_records_with_geometry'), 1)
        quota += 1
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_ds.dataframe.the_geom)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())
        self.assertTrue('cartodb_id' in gc_ds.dataframe)
        self.assertEqual(gc_ds.dataframe.index.name, 'cartodb_id')

    def test_geocode_query_as_new_table(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        ds = Dataset("SELECT 'Gran Via 46' AS address, 'Madrid' AS city", credentials=self.credentials)

        quota = self.used_quota(gc)

        table_name = self.get_test_table_name('gcdfds')

        # Preview
        info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'},
                          table_name=table_name, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_ds, info = gc.geocode(ds, street='address', city='city', country={'value': 'Spain'}, table_name=table_name)
        self.assertTrue(isinstance(gc_ds, Dataset))
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(info.get('successfully_geocoded'), 1)
        self.assertEqual(info.get('final_records_with_geometry'), 1)
        quota += 1
        self.assertEqual(self.used_quota(gc), quota)
        self.assertTrue('cartodb_id' in gc_ds.get_column_names())

    def test_geocode_dataframe_with_default_status(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        self.assertIsNotNone(gc_df.gc_status_rel)
        expected_columns = [RESERVED_GEO_COLUMN_NAME, 'address', 'carto_geocode_hash', 'cartodb_id', 'city',
                            'gc_status_rel', 'the_geom']
        self.assertEqual(sorted(gc_df.columns), expected_columns)

    def test_geocode_dataframe_with_json_status(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          status={'meta': '*'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status={'meta': '*'})
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        self.assertIsNotNone(gc_df.meta)
        self.assertEqual(sorted(gc_df['meta'].apply(json.loads)[1].keys()), ['match_types', 'precision', 'relevance'])
        expected_columns = [RESERVED_GEO_COLUMN_NAME, 'address', 'carto_geocode_hash', 'cartodb_id', 'city', 'meta',
                            'the_geom']
        self.assertEqual(sorted(gc_df.columns), expected_columns)

    def test_geocode_dataframe_with_json_legacy_status(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          status='meta', dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status='meta')
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        self.assertIsNotNone(gc_df.meta)
        self.assertEqual(sorted(gc_df['meta'].apply(json.loads)[1].keys()), ['match_types', 'precision', 'relevance'])
        expected_columns = [RESERVED_GEO_COLUMN_NAME, 'address', 'carto_geocode_hash', 'cartodb_id', 'city', 'meta',
                            'the_geom']
        self.assertEqual(sorted(gc_df.columns), expected_columns)

    def test_geocode_dataframe_with_no_status(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          status=None, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status=None)
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        expected_columns = [RESERVED_GEO_COLUMN_NAME, 'address', 'carto_geocode_hash', 'cartodb_id', 'city', 'the_geom']
        self.assertEqual(sorted(gc_df.columns), expected_columns)

    def test_geocode_dataframe_with_custom_status(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        status = {'gc_rel': 'relevance'}

        # Preview
        info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'},
                          status=status, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status=status)
        self.assertTrue(isinstance(gc_df, pd.DataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        self.assertIsNotNone(gc_df.gc_rel)
        expected_columns = [RESERVED_GEO_COLUMN_NAME, 'address', 'carto_geocode_hash', 'cartodb_id', 'city', 'gc_rel',
                            'the_geom']
        self.assertEqual(sorted(gc_df.columns), expected_columns)

    def test_geocode_dataframe_fails_with_invalid_status_fields(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        status = {'relevance': 'xyz'}

        with self.assertRaises(ValueError):
            gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status=status)
        self.assertEqual(self.used_quota(gc), quota)

    def test_geocode_dataframe_cached(self):
        self.skip(if_no_credits=True, if_no_credentials=True)
        gc = Geocoding(credentials=self.credentials)

        df = pd.DataFrame([['Gran Via 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        quota = self.used_quota(gc)

        table_name = self.get_test_table_name('cache')

        # Preview
        info = gc.geocode(
            df, cached=table_name, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode
        gc_df, info = gc.geocode(df, cached=table_name, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        self.assertEqual(info.get('required_quota'), 2)
        self.assertEqual(info.get('successfully_geocoded'), 2)
        self.assertEqual(info.get('final_records_with_geometry'), 2)
        quota += 2
        self.assertEqual(self.used_quota(gc), quota)
        self.assertIsNotNone(gc_df.the_geom)
        # self.assertFalse('cartodb_id' in gc_df)
        # self.assertNotEqual(gc_df.index.name, 'cartodb_id')

        sgc_df = gc_df

        # Preview, Geocode again (should do nothing)
        info = gc.geocode(
            df, cached=table_name, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)
        gc_df, info = gc.geocode(df, cached=table_name, street='address', city='city', country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        self.assertIsNotNone(gc_df.the_geom)
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)

        # Incremental geocoding: modify one row
        df.at[1, 'address'] = 'Gran Via 48'
        info = gc.geocode(
            df, cached=table_name, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 1)
        self.assertEqual(self.used_quota(gc), quota)
        gc_df, info = gc.geocode(
            df, cached=table_name, street='address', city={'column': 'city'}, country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        self.assertIsNotNone(gc_df.the_geom)
        self.assertEqual(info.get('required_quota'), 1)
        quota += 1
        self.assertEqual(self.used_quota(gc), quota)

        # Geocode unmodified geocoded gdf not using cache, because it has the hash column
        info = gc.geocode(
            sgc_df, cached=table_name, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)
        gc_df, info = gc.geocode(
            sgc_df, cached=table_name, street='address', city={'column': 'city'}, country={'value': 'Spain'})
        self.assertTrue(isinstance(gc_df, gpd.GeoDataFrame))
        self.assertIsNotNone(gc_df.the_geom)
        self.assertEqual(info.get('required_quota'), 0)
        self.assertEqual(self.used_quota(gc), quota)

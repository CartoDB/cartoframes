# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.Dataset"""
import json
import os
import sys
import unittest
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd

from carto.exceptions import CartoException

from cartoframes.auth import Credentials
from cartoframes.data import Dataset
from cartoframes.data.clients import SQLClient
from cartoframes.data.dataset.registry.base_dataset import BaseDataset
from cartoframes.data.dataset.registry.strategies_registry import StrategiesRegistry
from cartoframes.data.dataset.registry.dataframe_dataset import (
    DataFrameDataset, _rows)
from cartoframes.data.dataset.registry.query_dataset import QueryDataset
from cartoframes.data.dataset.registry.table_dataset import TableDataset
from cartoframes.lib import context
from cartoframes.utils.columns import DataframeColumnsInfo, normalize_name
from cartoframes.utils.geom_utils import setting_value_exception
from cartoframes.utils.utils import load_geojson
from tests.e2e.helpers import _UserUrlLoader
from tests.unit.mocks.context_mock import ContextMock
from tests.unit.mocks.dataset_mock import DatasetMock, QueryDatasetMock

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


WILL_SKIP = False
warnings.filterwarnings('ignore')


class TestDataset(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.CARTOframes"""

    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('tests/e2e/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except Exception:
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

        # table naming info
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        has_gpd = 'gpd' if os.environ.get('USE_GEOPANDAS') else 'nongpd'
        pyver = sys.version[0:3].replace('.', '_')
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER') or 'none'

        test_slug = '{ver}_{num}_{mpl}_{gpd}'.format(
            ver=pyver, num=buildnum, mpl=has_mpl, gpd=has_gpd
        )

        # for writing to carto
        self.test_write_table = normalize_name(
            'cf_test_table_{}'.format(test_slug)
        )

        self.base_url = self.user_url().format(username=self.username)
        self.credentials = Credentials(self.username, self.apikey, self.base_url)
        self.sql_client = SQLClient(self.credentials)

        self.test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -3.1640625,
                            42.032974332441405
                        ]
                    }
                }
            ]
        }

        self.tearDown()

    def tearDown(self):
        """restore to original state"""
        tables = (self.test_write_table, )
        sql_drop = 'DROP TABLE IF EXISTS {};'

        for table in tables:
            try:
                Dataset(table, credentials=self.credentials).delete()
                self.sql_client.query(sql_drop.format(table))
            except CartoException:
                warnings.warn('Error deleting tables')

        StrategiesRegistry.instance = None

    def test_dataset_upload_validation_fails_only_with_table_name(self):
        table_name = 'fake_table'
        dataset = Dataset(table_name, credentials=self.credentials)
        err_msg = 'Nothing to upload. We need data in a DataFrame or GeoDataFrame or a query to upload data to CARTO.'
        with self.assertRaises(ValueError, msg=err_msg):
            dataset.upload()

    def test_dataset_upload_validation_query_fails_without_table_name(self):
        query = 'SELECT 1'
        dataset = Dataset(query, credentials=self.credentials)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload()

    def test_dataset_upload_validation_df_fails_without_table_name_and_context(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset(df)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload()

    def test_dataset_upload_validation_df_fails_without_context(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset(df)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload(table_name=self.test_write_table)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_upload_into_existing_table_fails_without_replace_property(self):
        query = 'SELECT 1'
        dataset = Dataset(query, credentials=self.credentials)
        dataset.upload(table_name=self.test_write_table)

        dataset = Dataset(query, credentials=self.credentials)
        err_msg = ('Table with name {t} and schema {s} already exists in CARTO. Please choose a different `table_name`'
                   'or use if_exists="replace" to overwrite it').format(t=self.test_write_table, s='public')
        with self.assertRaises(CartoException, msg=err_msg):
            dataset.upload(table_name=self.test_write_table)
        dataset.upload(table_name=self.test_write_table, if_exists=Dataset.IF_EXISTS_REPLACE)

    def test_dataset_upload_validation_fails_with_query_and_append(self):
        query = 'SELECT 1'
        dataset = Dataset(query, credentials=self.credentials)
        err_msg = 'Error using append with a query Dataset. It is not possible to append data to a query'
        with self.assertRaises(CartoException, msg=err_msg):
            dataset.upload(table_name=self.test_write_table, if_exists=Dataset.IF_EXISTS_APPEND)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_download_validations(self):
        self.assertNotExistsTable(self.test_write_table)

        df = load_geojson(self.test_geojson)
        dataset = Dataset(df)
        error_msg = 'You should provide a context and a table_name or query to download data.'
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.download()

        query = 'SELECT 1 as fakec'
        dataset = Dataset(query, credentials=self.credentials)
        dataset.upload(table_name=self.test_write_table)

        dataset._table_name = 'non_used_table'
        df = dataset.download()
        self.assertEqual('fakec' in df.columns, True)

        dataset = Dataset(self.test_write_table, credentials=self.credentials)
        df = dataset.download()
        self.assertEqual('fakec' in df.columns, True)

    def test_dataset_download_and_upload(self):
        self.assertNotExistsTable(self.test_write_table)

        query = 'SELECT 1 as fakec'
        dataset = Dataset(query, credentials=self.credentials)
        df = dataset.download()

        dataset = Dataset(df)
        dataset.upload(table_name=self.test_write_table,
                       credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        dataset = Dataset(self.test_write_table, credentials=self.credentials)
        df = dataset.download()

        dataset = Dataset(df)
        dataset.upload(table_name=self.test_write_table,
                       credentials=self.credentials,
                       if_exists=Dataset.IF_EXISTS_REPLACE)

    def test_dataset_upload_and_download_special_values(self):
        self.assertNotExistsTable(self.test_write_table)

        orig_df = pd.DataFrame({
            'lat': [0, 1, 2],
            'lng': [0, 1, 2],
            'svals': [np.inf, -np.inf, np.nan]
        })

        dataset = Dataset(orig_df)
        dataset.upload(table_name=self.test_write_table,
                       with_lnglat=('lng', 'lat'),
                       credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        dataset = Dataset(self.test_write_table, credentials=self.credentials)
        df = dataset.download()

        assert df.lat.equals(orig_df.lat)
        assert df.lng.equals(orig_df.lng)
        assert df.svals.equals(orig_df.svals)
        assert df.the_geom.notnull().all()

    def test_dataset_download_bool_null(self):
        self.assertNotExistsTable(self.test_write_table)

        query = 'SELECT * FROM (values (true, true), (false, false), (false, null)) as x(fakec_bool, fakec_bool_null)'
        dataset = Dataset(query, credentials=self.credentials)
        dataset.upload(table_name=self.test_write_table)

        dataset = Dataset(self.test_write_table, credentials=self.credentials)
        df = dataset.download()

        self.assertEqual(df['fakec_bool'].dtype, 'bool')
        self.assertEqual(df['fakec_bool_null'].dtype, 'object')
        self.assertEqual(list(df['fakec_bool']), [True, False, False])
        self.assertEqual(list(df['fakec_bool_null']), [True, False, None])

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_points_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_mcdonalds_nyc
        df = read_mcdonalds_nyc(limit=100)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_lines_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_ne_50m_graticules_15
        df = read_ne_50m_graticules_15()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 35)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_polygons_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_lnglat_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=50)
        lnglat = ('dropoff_longitude', 'dropoff_latitude')
        Dataset(df).upload(with_lnglat=lnglat, table_name=self.test_write_table, credentials=self.credentials)
        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_null_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=10)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom_webmercator IS NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 10)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_with_different_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        df.rename(columns={'the_geom': 'geometry'}, inplace=True)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_with_different_geom_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()

        df.rename(columns={'the_geom': 'geom'}, inplace=True)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_geopandas(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        import shapely
        df = read_taxi(limit=50)
        df.drop(['the_geom'], axis=1, inplace=True)
        gdf = gpd.GeoDataFrame(df.drop(['dropoff_longitude', 'dropoff_latitude'], axis=1),
                               crs={'init': 'epsg:4326'},
                               geometry=[shapely.geometry.Point(xy) for xy in
                                         zip(df.dropoff_longitude, df.dropoff_latitude)])

        # TODO: use from_geodataframe
        dataset = Dataset(gdf).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_wkt(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=50)
        df['the_geom'] = df.apply(lambda x: 'POINT ({x} {y})'
                                  .format(x=x['dropoff_longitude'], y=x['dropoff_latitude']), axis=1)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_fail_by_default(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        err_msg = ('Table with name {t} and schema {s} already exists in CARTO. Please choose a different `table_name`'
                   'or use if_exists="replace" to overwrite it').format(t=self.test_write_table, s='public')
        with self.assertRaises(CartoException, msg=err_msg):
            dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_append(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)

        # avoid uploading the same index or cartodb_id
        df.index += df.index.max() + 1
        df['cartodb_id'] += df['cartodb_id'].max() + 1

        Dataset(df).upload(if_exists=Dataset.IF_EXISTS_APPEND,
                           table_name=self.test_write_table,
                           credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052 * 2)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_replace(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        dataset = Dataset(df).upload(
            if_exists=Dataset.IF_EXISTS_REPLACE, table_name=self.test_write_table, credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2052)

    def test_dataset_schema_from_parameter(self):
        schema = 'fake_schema'
        dataset = Dataset('fake_table', schema=schema, credentials=self.credentials)
        self.assertEqual(dataset.schema, schema)

    def test_dataset_schema_from_non_org_context(self):
        dataset = Dataset('fake_table', credentials=self.credentials)
        self.assertEqual(dataset.schema, 'public')

    def test_dataset_schema_from_org_context(self):
        pass
        # dataset = DatasetMock('fake_table', credentials=self.credentials)
        # self.assertEqual(dataset.schema, 'fake_username')

    # FIXME does not work in python 2.7 (COPY stucks and blocks the table, fix after
    # https://github.com/CartoDB/CartoDB-SQL-API/issues/579 is fixed)
    # @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    # def test_dataset_write_with_encoding(self):
    #     df = pd.DataFrame({'vals': [1, 2], 'strings': ['a', 'ô']})
    #     dataset = self.con.write(df, self.test_write_table)
    #     self.test_write_table = dataset.table_name

    #     self.assertExistsTable(self.test_write_table)

    def assertExistsTable(self, table_name):
        resp = self.sql_client.query('''
            SELECT *
            FROM {table}
            LIMIT 0
            '''.format(table=table_name))
        self.assertIsNotNone(resp)

    def assertNotExistsTable(self, table_name):
        try:
            self.sql_client.query('''
                SELECT *
                FROM {table}
                LIMIT 0
                '''.format(table=table_name))
        except CartoException as e:
            self.assertTrue('relation "{}" does not exist'.format(table_name) in str(e))


class TestDatasetInfo(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

        self._context_mock = ContextMock()
        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock

    def tearDown(self):
        context.create_context = self.original_create_context

    def test_dataset_info_should_work_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVACY_PRIVATE)

    def test_dataset_get_privacy_from_new_table(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')

        dataset = DatasetMock('fake_table', credentials=self.credentials)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVACY_PRIVATE)

    def test_dataset_set_privacy_to_new_table(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')

        dataset = DatasetMock('fake_table', credentials=self.credentials)
        dataset.update_dataset_info(privacy=Dataset.PRIVACY_PUBLIC)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVACY_PUBLIC)

    def test_dataset_set_privacy_with_wrong_parameter(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')
        wrong_privacy = 'wrong_privacy'
        error_msg = 'Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
            p=wrong_privacy, o1=Dataset.PRIVACY_PRIVATE, o2=Dataset.PRIVACY_PUBLIC, o3=Dataset.PRIVACY_LINK)
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.update_dataset_info(privacy=wrong_privacy)

    def test_dataset_info_props_are_private(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)
        dataset_info = dataset.dataset_info
        self.assertEqual(dataset_info.privacy, Dataset.PRIVACY_PRIVATE)
        privacy = Dataset.PRIVACY_PUBLIC
        error_msg = str(setting_value_exception('privacy', privacy))
        with self.assertRaises(CartoException, msg=error_msg):
            dataset_info.privacy = privacy
        self.assertEqual(dataset_info.privacy, Dataset.PRIVACY_PRIVATE)

    def test_dataset_info_from_dataframe(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        dataset = DatasetMock(df)
        error_msg = ('Your data is not synchronized with CARTO.'
                     'First of all, you should call upload method '
                     'to save your data in CARTO.')
        with self.assertRaises(CartoException, msg=error_msg):
            self.assertIsNotNone(dataset.dataset_info)

    def test_dataset_info_from_dataframe_sync(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        dataset = DatasetMock(df)
        dataset.upload(table_name='fake_table', credentials=self.credentials)

        dataset = DatasetMock('fake_table', credentials=self.credentials)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVACY_PRIVATE)

    def test_dataset_info_from_query(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        error_msg = ('We can not extract Dataset info from a QueryDataset. Use a TableDataset '
                     '`Dataset(table_name)` to get or modify the info from a CARTO table.')
        with self.assertRaises(ValueError, msg=error_msg):
            self.assertIsNotNone(dataset.dataset_info)

    def test_dataset_info_from_query_update(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        error_msg = ('We can not extract Dataset info from a QueryDataset. Use a TableDataset '
                     '`Dataset(table_name)` to get or modify the info from a CARTO table.')
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.update_dataset_info()


class TestDatasetUnit(unittest.TestCase, _UserUrlLoader):
    """Unit tests for cartoframes.Dataset"""

    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)
        self.test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -3.1640625,
                            42.032974332441405
                        ]
                    }
                }
            ]
        }

        self._context_mock = ContextMock()
        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock

    def tearDown(self):
        StrategiesRegistry.instance = None
        context.create_context = self.original_create_context

    def assertIsTableDatasetInstance(self, table_name):
        ds = DatasetMock(table_name, credentials=self.credentials)
        error = "Dataset('{}')._strategy is not an instance of TableDataset".format(table_name)
        self.assertTrue(isinstance(ds._strategy, TableDataset), msg=error)

    def assertIsQueryDatasetInstance(self, query):
        ds = DatasetMock(query, credentials=self.credentials)
        error = "Dataset('{}')._strategy is not an instance of QueryDataset".format(query)
        self.assertTrue(isinstance(ds._strategy, QueryDataset), msg=error)

    def assertIsDataFrameDatasetInstance(self, data):
        ds = DatasetMock(data)
        error = "Dataset('{}')._strategy is not an instance of DataFrameDataset".format(data)
        self.assertTrue(isinstance(ds._strategy, DataFrameDataset), msg=error)

    def test_creation_from_valid_table_names(self):
        table_names = ['myt', 'my_t', 'tgeojson', 't_geojson', 'geojson', 'json', 'select_t']
        for table_name in table_names:
            self.assertIsTableDatasetInstance(table_name)

    def test_creation_from_valid_queries(self):
        queries = ['SELECT * FROM', 'select * from', 'select c', 'with n as', 'WITH n AS', 'select * from json',
                   'select * from geojson']
        for query in queries:
            self.assertIsQueryDatasetInstance(query)

    def test_creation_from_valid_dataframe(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        self.assertIsDataFrameDatasetInstance(df)

    def test_creation_from_valid_geodataframe(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        gdf = gpd.GeoDataFrame(df)
        self.assertIsDataFrameDatasetInstance(gdf)

    def test_creation_from_valid_localgeojson(self):
        self.assertIsDataFrameDatasetInstance(self.test_geojson)

    def test_creation_from_valid_geojson_file_path(self):
        paths = [os.path.abspath('tests/e2e/data/dataset/fixtures/valid.geojson'),
                 os.path.abspath('tests/e2e/data/dataset/fixtures/validgeo.json')]
        for path in paths:
            self.assertIsDataFrameDatasetInstance(path)

    def test_creation_from_wrong_geojson_file_path(self):
        geojson_file_path = os.path.abspath('tests/e2e/data/dataset/fixtures/wrong.geojson')
        with self.assertRaises(Exception):
            self.assertIsDataFrameDatasetInstance(geojson_file_path)

    def test_creation_from_unexisting_geojson_file_path(self):
        geojson_file_path = os.path.abspath('unexisting.geojson')
        with self.assertRaises(ValueError, msg='We can not detect the Dataset type'):
            self.assertIsDataFrameDatasetInstance(geojson_file_path)

    def test_dataset_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.table_name, table_name)
        self.assertEqual(dataset.schema, 'public')
        self.assertEqual(dataset.credentials, self.credentials)

    def test_dataset_from_query(self):
        query = 'SELECT * FROM fake_table'
        dataset = DatasetMock(query, credentials=self.credentials)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.query, query)
        self.assertEqual(dataset.credentials, self.credentials)
        self.assertIsNone(dataset.table_name)

    def test_dataset_from_dataframe(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset(df)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.dataframe)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.credentials)

    def test_dataset_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = Dataset(gdf)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.dataframe)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.credentials)

    def test_dataset_from_geojson(self):
        geojson = self.test_geojson
        dataset = Dataset(geojson)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.dataframe)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.credentials)

    def test_dataset_from_table_without_credentials(self):
        table_name = 'fake_table'
        error_msg = ('Credentials attribute is required. '
                     'Please pass a `Credentials` instance '
                     'or use the `set_default_credentials` function.')
        with self.assertRaises(AttributeError, msg=error_msg):
            Dataset(table_name)

    def test_dataset_from_query_without_credentials(self):
        query = 'SELECT * FROM fake_table'
        error_msg = ('Credentials attribute is required. '
                     'Please pass a `Credentials` instance '
                     'or use the `set_default_credentials` function.')
        with self.assertRaises(AttributeError, msg=error_msg):
            Dataset(query)

    def test_dataset_get_table_names_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)
        self.assertEqual(dataset.get_table_names(), [table_name])

    def test_dataset_get_table_names_from_query(self):
        table_name = 'fake_table'

        QueryDatasetMock.get_table_names = Mock(return_value=[table_name])

        query = 'SELECT * FROM {}'.format(table_name)
        dataset = DatasetMock(query, credentials=self.credentials)
        self.assertEqual(dataset.get_table_names(), [table_name])

    def test_dataset_get_table_names_from_dataframe(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset(df)
        error_msg = ('Your data is not synchronized with CARTO.'
                     'First of all, you should call upload method '
                     'to save your data in CARTO.')
        with self.assertRaises(CartoException, msg=error_msg):
            dataset.get_table_names()

    def test_create_table_query(self):
        df = pd.DataFrame.from_dict({'cartodb_id': [1], 'the_geom': ['POINT (1 1)']})
        dataframe_columns_info = DataframeColumnsInfo(df, None)
        table_name = 'fake_table'
        expected_result = 'CREATE TABLE {} (cartodb_id bigint, the_geom geometry(Point, 4326))'.format(table_name)

        dataset = DataFrameDataset(df)
        dataset.table_name = table_name
        result = dataset._create_table_query(dataframe_columns_info.columns)
        self.assertEqual(result, expected_result)

    def test_create_table_query_without_geom(self):
        df = pd.DataFrame.from_dict({'cartodb_id': [1]})
        dataframe_columns_info = DataframeColumnsInfo(df, None)
        table_name = 'fake_table'
        expected_result = 'CREATE TABLE {} (cartodb_id bigint)'.format(table_name)

        dataset = DataFrameDataset(df)
        dataset.table_name = table_name
        result = dataset._create_table_query(dataframe_columns_info.columns)
        self.assertEqual(result, expected_result)

    def test_create_table_query_with_several_geometry_columns_prioritize_the_geom(self):
        df = pd.DataFrame([['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']], columns=['geom', 'the_geom', 'geometry'])
        dataframe_columns_info = DataframeColumnsInfo(df, None)
        table_name = 'fake_table'
        expected_result = 'CREATE TABLE {} (geom text, the_geom geometry(Point, 4326), geometry text)'.format(
            table_name)

        dataset = DataFrameDataset(df)
        dataset.table_name = table_name
        result = dataset._create_table_query(dataframe_columns_info.columns)
        self.assertEqual(result, expected_result)

    def test_create_table_query_with_several_geometry_columns_and_geodataframe_prioritize_geometry(self):
        df = pd.DataFrame([['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']], columns=['geom', 'the_geom', 'geometry'])
        from shapely.wkt import loads
        df['geometry'] = df['geometry'].apply(loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        dataframe_columns_info = DataframeColumnsInfo(gdf, None)
        table_name = 'fake_table'
        expected_result = 'CREATE TABLE {} (geom text, the_geom geometry(Point, 4326))'.format(table_name)

        dataset = DataFrameDataset(gdf)
        dataset.table_name = table_name
        result = dataset._create_table_query(dataframe_columns_info.columns)
        self.assertEqual(result, expected_result)

    def test_dataset_upload_one_geometry_that_is_not_the_geom_uses_the_geom(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([['POINT (1 1)']], columns=['geom'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(the_geom,cartodb_id) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'SRID=4326;POINT (1 1)|0\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_one_geometry_that_is_the_geom_uses_the_geom(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([['POINT (1 1)']], columns=['the_geom'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(the_geom,cartodb_id) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'SRID=4326;POINT (1 1)|0\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_with_several_geometry_columns_prioritize_the_geom(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']], columns=['geom', 'the_geom', 'geometry'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = ("COPY {}(geom,the_geom,geometry,cartodb_id)"
                          " FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');").format(table)
        expected_data = [b'POINT (0 0)|SRID=4326;POINT (1 1)|POINT (2 2)|0\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_with_several_geometry_columns_and_geodataframe_prioritize_geometry(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']], columns=['geom', 'the_geom', 'geometry'])
        from shapely.wkt import loads
        df['geometry'] = df['geometry'].apply(loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        ds = Dataset(gdf)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(geom,the_geom,cartodb_id) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'POINT (0 0)|SRID=4326;POINT (2 2)|0\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_the_geom_webmercator_column_is_removed(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([[1, 'POINT (1 1)', 'fake']], columns=['cartodb_id', 'the_geom', 'the_geom_webmercator'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(cartodb_id,the_geom) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'1|SRID=4326;POINT (1 1)\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_with_lng_lat(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([[1, 1]], columns=['lng', 'lat'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials, with_lnglat=('lng', 'lat'))

        expected_query = ("COPY {}(lng,lat,cartodb_id,the_geom)"
                          " FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');").format(table)
        expected_data = [b'1|1|0|SRID=4326;POINT (1 1)\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_prioritizing_with_lng_lat_over_the_geom(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([[1, 1, 'POINT (2 2)']], columns=['lng', 'lat', 'the_geom'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials, with_lnglat=('lng', 'lat'))

        expected_query = """
        COPY {}(lng,lat,cartodb_id,the_geom) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'1|1|0|SRID=4326;POINT (1 1)\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_prioritizing_with_lng_lat_over_other_geom_names(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([[1, 1, 'POINT (2 2)']], columns=['lng', 'lat', 'geometry'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials, with_lnglat=('lng', 'lat'))

        expected_query = """
        COPY {}(lng,lat,cartodb_id,the_geom) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'1|1|0|SRID=4326;POINT (1 1)\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_without_geom(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame([[1, True, 'text']], columns=['col1', 'col2', 'col3'])
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(col1,col2,col3,cartodb_id) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'1|True|text|0\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)

    def test_dataset_upload_null_values(self):
        table = 'fake_table'
        credentials = 'fake'
        df = pd.DataFrame.from_dict({'test': [None, None]})
        ds = Dataset(df)

        BaseDataset.exists = Mock(return_value=False)

        ds.upload(table_name=table, credentials=credentials)

        expected_query = """
        COPY {}(test,cartodb_id) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        """.format(table).strip()
        expected_data = [b'__null|0\n', b'__null|1\n']

        self.assertEqual(ds._strategy._context.query, expected_query)
        self.assertEqual(list(ds._strategy._context.response), expected_data)


class TestDataFrameDatasetUnit(unittest.TestCase, _UserUrlLoader):
    def test_rows(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        with_lnglat = None
        dataframe_columns_info = DataframeColumnsInfo(df, with_lnglat)
        rows = _rows(df, dataframe_columns_info, with_lnglat)

        self.assertEqual(list(rows), [b'True\n', b'[1, 2]\n'])

    def test_rows_null(self):
        df = pd.DataFrame.from_dict({'test': [None]})
        with_lnglat = None
        dataframe_columns_info = DataframeColumnsInfo(df, with_lnglat)
        rows = _rows(df, dataframe_columns_info, with_lnglat)

        self.assertEqual(list(rows), [b'__null\n'])

    def test_rows_with_geom(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]], 'the_geom': ['Point (0 0)', 'Point (1 1)']})
        with_lnglat = None
        dataframe_columns_info = DataframeColumnsInfo(df, with_lnglat)
        rows = _rows(df, dataframe_columns_info, with_lnglat)

        self.assertEqual(list(rows), [b'True|SRID=4326;POINT (0 0)\n', b'[1, 2]|SRID=4326;POINT (1 1)\n'])

    def test_rows_null_geom(self):
        df = pd.DataFrame.from_dict({'test': [None], 'the_geom': [None]})
        with_lnglat = None
        dataframe_columns_info = DataframeColumnsInfo(df, with_lnglat)
        rows = _rows(df, dataframe_columns_info, with_lnglat)

        self.assertEqual(list(rows), [b'__null|SRID=4326;GEOMETRYCOLLECTION EMPTY\n'])

    def test_rows_non_ascii(self):
        attribute = 'áéí'
        unicode_attribute = u'áéí'
        encoded_attribute = unicode_attribute.encode('utf-8')
        encoded_line = encoded_attribute + '\n'.encode()

        df = pd.DataFrame.from_dict({'test': [attribute, unicode_attribute, encoded_attribute, 'xyz']})
        columns_info = DataframeColumnsInfo(df)
        rows = _rows(df, columns_info, None)
        self.assertEqual(list(rows), [encoded_line, encoded_line, encoded_line, b'xyz\n'])

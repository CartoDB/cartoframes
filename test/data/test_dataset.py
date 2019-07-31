# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.Dataset"""
import unittest
import os
import sys
import json
import warnings
import pandas as pd

from carto.exceptions import CartoException

from cartoframes.data import Dataset
from cartoframes.auth import Credentials
from cartoframes.client import SQLClient
from cartoframes.data.utils import setting_value_exception
from cartoframes.data.columns import normalize_name
from cartoframes.utils import load_geojson
from cartoframes.data import StrategiesRegistry
from cartoframes.data.registry.dataframe_dataset import DataFrameDataset, _rows
from cartoframes.data.registry.table_dataset import TableDataset
from cartoframes.data.registry.query_dataset import QueryDataset
from cartoframes import context

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from ..mocks.dataset_mock import DatasetMock, QueryDatasetMock
from ..mocks.context_mock import ContextMock

from ..utils import _UserUrlLoader

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

WILL_SKIP = False
warnings.filterwarnings('ignore')


class TestDataset(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.CARTOframes"""

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
        WILL_SKIP = self.apikey is None or self.username is None  # noqa: F841

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
        dataset.upload(table_name=self.test_write_table, if_exists=Dataset.REPLACE)

    def test_dataset_upload_validation_fails_with_query_and_append(self):
        query = 'SELECT 1'
        dataset = Dataset(query, credentials=self.credentials)
        err_msg = 'Error using append with a query Dataset. It is not possible to append data to a query'
        with self.assertRaises(CartoException, msg=err_msg):
            dataset.upload(table_name=self.test_write_table, if_exists=Dataset.APPEND)

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
        dataset.upload(table_name=self.test_write_table)

        dataset = Dataset(self.test_write_table, credentials=self.credentials)
        dataset.download()
        dataset.upload(table_name=self.test_write_table, if_exists=Dataset.REPLACE)

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
        print(result)
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
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_lnglat_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        lnglat = ('dropoff_longitude', 'dropoff_latitude')
        dataset = Dataset(df).upload(
            with_lnglat=lnglat, table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_null_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 100)

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
        self.assertEqual(result['total_rows'], 2049)

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
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_geopandas(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        import shapely
        import geopandas as gpd
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
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_append(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        dataset = Dataset(df).upload(
            if_exists=Dataset.APPEND, table_name=self.test_write_table, credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2049 * 2)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_replace(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(df).upload(table_name=self.test_write_table, credentials=self.credentials)
        self.test_write_table = dataset.table_name

        dataset = Dataset(df).upload(
            if_exists=Dataset.REPLACE, table_name=self.test_write_table, credentials=self.credentials)

        self.assertExistsTable(self.test_write_table)

        query = 'SELECT cartodb_id FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table)
        result = self.sql_client.query(query, verbose=True)
        self.assertEqual(result['total_rows'], 2049)

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
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVATE)

    def test_dataset_get_privacy_from_new_table(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVATE)

    def test_dataset_set_privacy_to_new_table(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')
        dataset.update_dataset_info(privacy=Dataset.PUBLIC)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PUBLIC)

    def test_dataset_set_privacy_with_wrong_parameter(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset.upload(table_name='fake_table')
        wrong_privacy = 'wrong_privacy'
        error_msg = 'Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
            p=wrong_privacy, o1=Dataset.PRIVATE, o2=Dataset.PUBLIC, o3=Dataset.LINK)
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.update_dataset_info(privacy=wrong_privacy)

    def test_dataset_info_props_are_private(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)
        dataset_info = dataset.dataset_info
        self.assertEqual(dataset_info.privacy, Dataset.PRIVATE)
        privacy = Dataset.PUBLIC
        error_msg = str(setting_value_exception('privacy', privacy))
        with self.assertRaises(CartoException, msg=error_msg):
            dataset_info.privacy = privacy
        self.assertEqual(dataset_info.privacy, Dataset.PRIVATE)

    def test_dataset_info_from_dataframe(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        dataset = DatasetMock(df)
        error_msg = ('Your data is not synchronized with CARTO.'
                     'First of all, you should call upload method '
                     'to save your data in CARTO.')
        with self.assertRaises(CartoException, msg=error_msg):
            dataset.dataset_info

    def test_dataset_info_from_dataframe_sync(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        dataset = DatasetMock(df)
        dataset.upload(table_name='fake_table', credentials=self.credentials)
        self.assertEqual(dataset.dataset_info.privacy, Dataset.PRIVATE)

    def test_dataset_info_from_query(self):
        query = 'SELECT 1'
        dataset = DatasetMock(query, credentials=self.credentials)
        error_msg = ('We can not extract Dataset info from a QueryDataset. Use a TableDataset '
                     '`Dataset(table_name)` to get or modify the info from a CARTO table.')
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.dataset_info

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

    @unittest.skipIf(not HAS_GEOPANDAS, 'no geopandas imported, skipping this test')
    def test_creation_from_valid_geodataframe(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        gdf = geopandas.GeoDataFrame(df)
        self.assertIsDataFrameDatasetInstance(gdf)

    def test_creation_from_valid_localgeojson(self):
        self.assertIsDataFrameDatasetInstance(self.test_geojson)

    def test_creation_from_invalid_localgeojson(self):
        geojson = object
        with self.assertRaises(ValueError, msg='We can not detect the Dataset type'):
            self.assertIsDataFrameDatasetInstance(geojson)

    def test_creation_from_valid_geojson_file_path(self):
        paths = [os.path.abspath('test/fixtures/valid.geojson'), os.path.abspath('test/fixtures/validgeo.json')]
        for path in paths:
            self.assertIsDataFrameDatasetInstance(path)

    def test_creation_from_wrong_geojson_file_path(self):
        geojson_file_path = os.path.abspath('test/fixtures/wrong.geojson')
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


class TestDataFrameDatasetUnit(unittest.TestCase, _UserUrlLoader):
    def test_rows(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]]})
        rows = _rows(df, ['test'], None, '', '')

        self.assertEqual(list(rows), [b'True\n', b'[1, 2]\n'])

    def test_rows_null(self):
        df = pd.DataFrame.from_dict({'test': [None, [None, None]]})
        rows = _rows(df, ['test'], None, '', '')

        self.assertEqual(list(rows), [b'\n', b'\n'])

    def test_rows_with_geom(self):
        df = pd.DataFrame.from_dict({'test': [True, [1, 2]], 'the_geom': [None, None]})
        rows = _rows(df, ['test'], None, '', '')

        self.assertEqual(list(rows), [b'True\n', b'[1, 2]\n'])

    def test_rows_null_geom(self):
        df = pd.DataFrame.from_dict({'test': [None, [None, None]], 'the_geom': [None, None]})
        rows = _rows(df, ['test'], None, '', '')

        self.assertEqual(list(rows), [b'\n', b'\n'])

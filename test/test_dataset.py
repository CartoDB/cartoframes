# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.context"""
import unittest
import os
import sys
import json
import warnings

from carto.exceptions import CartoException

from cartoframes.context import CartoContext
from cartoframes.dataset import Dataset, _decode_geom
from cartoframes.columns import normalize_name
from cartoframes.geojson import load_geojson

from utils import _UserUrlLoader

WILL_SKIP = False
warnings.filterwarnings("ignore")


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
                warnings.warn("Skipping CartoContext tests. To test it, "
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

        self.baseurl = self.user_url().format(username=self.username)
        self.cc = CartoContext(base_url=self.baseurl, api_key=self.apikey)

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

        if self.apikey and self.baseurl:
            for table in tables:
                try:
                    self.cc.delete(table)
                    self.cc.sql_client.send(sql_drop.format(table))
                except CartoException:
                    warnings.warn('Error deleting tables')

    def test_dataset_constructor_validation_fails_with_table_name_and_query(self):
        table_name = 'fake_table'
        schema = 'fake_schema'
        query = 'select * from fake_table'
        with self.assertRaises(ValueError):
            Dataset(table_name=table_name, schema=schema, query=query)

    def test_dataset_constructor_validation_fails_with_table_name_and_dataframe(self):
        table_name = 'fake_table'
        schema = 'fake_schema'
        df = {}
        with self.assertRaises(ValueError):
            Dataset(table_name=table_name, schema=schema, df=df)

    def test_dataset_constructor_validation_fails_with_table_name_and_geodataframe(self):
        table_name = 'fake_table'
        schema = 'fake_schema'
        gdf = {}
        with self.assertRaises(ValueError):
            Dataset(table_name=table_name, schema=schema, gdf=gdf)

    def test_dataset_constructor_validation_fails_with_query_and_dataframe(self):
        query = 'select * from fake_table'
        df = {}
        with self.assertRaises(ValueError):
            Dataset(query=query, df=df)

    def test_dataset_constructor_validation_fails_with_dataframe_and_geodataframe(self):
        df = {}
        gdf = {}
        with self.assertRaises(ValueError):
            Dataset(df=df, gdf=gdf)

    def test_dataset_from_table(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.table_name, table_name)
        self.assertEqual(dataset.schema, 'public')
        self.assertIsNone(dataset.query)
        self.assertIsNone(dataset.df)
        self.assertIsNone(dataset.gdf)
        self.assertEqual(dataset.cc, self.cc)
        self.assertEqual(dataset.state, Dataset.STATE_REMOTE)

    def test_dataset_from_query(self):
        query = 'SELECT * FROM fake_table'
        dataset = Dataset.from_query(query=query, context=self.cc)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.query, query)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.df)
        self.assertIsNone(dataset.gdf)
        self.assertEqual(dataset.cc, self.cc)
        self.assertEqual(dataset.state, Dataset.STATE_REMOTE)

    def test_dataset_from_dataframe(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset.from_dataframe(df=df)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.df)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.query)
        self.assertIsNone(dataset.gdf)
        self.assertIsNone(dataset.cc)
        self.assertEqual(dataset.state, Dataset.STATE_LOCAL)

    def test_dataset_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = Dataset.from_geodataframe(gdf=gdf)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.gdf)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.query)
        self.assertIsNone(dataset.df)
        self.assertIsNone(dataset.cc)
        self.assertEqual(dataset.state, Dataset.STATE_LOCAL)

    def test_dataset_from_geojson(self):
        geojson = self.test_geojson
        dataset = Dataset.from_geojson(geojson=geojson)

        self.assertIsInstance(dataset, Dataset)
        self.assertIsNotNone(dataset.gdf)
        self.assertIsNone(dataset.table_name)
        self.assertIsNone(dataset.query)
        self.assertIsNone(dataset.df)
        self.assertIsNone(dataset.cc)
        self.assertEqual(dataset.state, Dataset.STATE_LOCAL)

    def test_dataset_upload_validation_fails_only_with_table_name(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        err_msg = 'Nothing to upload. We need data in a DataFrame or GeoDataFrame or a query to upload data to CARTO.'
        with self.assertRaises(ValueError, msg=err_msg):
            dataset.upload()

    def test_dataset_upload_validation_query_fails_without_table_name(self):
        query = 'SELECT 1'
        dataset = Dataset.from_query(query=query, context=self.cc)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload()

    def test_dataset_upload_validation_df_fails_without_table_name_and_context(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset.from_dataframe(df=df)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload()

    def test_dataset_upload_validation_df_fails_without_context(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset.from_dataframe(df=df)
        with self.assertRaises(ValueError, msg='You should provide a table_name and context to upload data.'):
            dataset.upload(table_name=self.test_write_table)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_upload_into_existing_table_fails_without_replace_property(self):
        query = 'SELECT 1'
        dataset = Dataset.from_query(query=query, context=self.cc)
        dataset.upload(table_name=self.test_write_table)
        err_msg = ('Table with name {t} and schema {s} already exists in CARTO. Please choose a different `table_name`'
                   'or use if_exists="replace" to overwrite it').format(t=self.test_write_table, s='public')
        with self.assertRaises(CartoException, msg=err_msg):
            dataset.upload(table_name=self.test_write_table)
        dataset.upload(table_name=self.test_write_table, if_exists=Dataset.REPLACE)

    def test_dataset_upload_validation_fails_with_query_and_append(self):
        query = 'SELECT 1'
        dataset = Dataset.from_query(query=query, context=self.cc)
        err_msg = 'Error using append with a query Dataset. It is not possible to append data to a query'
        with self.assertRaises(CartoException, msg=err_msg):
            dataset.upload(table_name=self.test_write_table, if_exists=Dataset.APPEND)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_download_validations(self):
        self.assertNotExistsTable(self.test_write_table)

        df = load_geojson(self.test_geojson)
        dataset = Dataset.from_dataframe(df=df)
        error_msg = 'You should provide a context and a table_name or query to download data.'
        with self.assertRaises(ValueError, msg=error_msg):
            dataset.download()

        query = 'SELECT 1 as fakec'
        dataset = Dataset.from_query(query=query, context=self.cc)
        dataset.upload(table_name=self.test_write_table)

        dataset.table_name = 'non_used_table'
        df = dataset.download()
        self.assertEqual('fakec' in df.columns, True)

        dataset = Dataset.from_table(table_name=self.test_write_table, context=self.cc)
        df = dataset.download()
        self.assertEqual('fakec' in df.columns, True)

    def test_dataset_download_and_upload(self):
        self.assertNotExistsTable(self.test_write_table)

        query = 'SELECT 1 as fakec'
        dataset = Dataset.from_query(query=query, context=self.cc)
        dataset.upload(table_name=self.test_write_table)

        dataset = Dataset.from_table(table_name=self.test_write_table, context=self.cc)
        dataset.download()
        dataset.upload(table_name=self.test_write_table, if_exists=Dataset.REPLACE)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_points_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_mcdonalds_nyc
        df = read_mcdonalds_nyc(limit=100)
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_lines_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_ne_50m_graticules_15
        df = read_ne_50m_graticules_15()
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 35)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_polygons_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_lnglat_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        lnglat = ('dropoff_longitude', 'dropoff_latitude')
        dataset = Dataset.from_dataframe(df).upload(
            with_lnglat=lnglat, table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_null_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_with_different_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        df.rename(columns={'the_geom': 'geometry'}, inplace=True)
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_with_different_geom_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()

        df.rename(columns={'the_geom': 'geom'}, inplace=True)
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
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
        dataset = Dataset.from_dataframe(gdf).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_wkt(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=50)
        df['the_geom'] = df.apply(lambda x: 'POINT ({x} {y})'
                                  .format(x=x['dropoff_longitude'], y=x['dropoff_latitude']), axis=1)
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_fail_by_default(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        err_msg = ('Table with name {t} and schema {s} already exists in CARTO. Please choose a different `table_name`'
                   'or use if_exists="replace" to overwrite it').format(t=self.test_write_table, s='public')
        with self.assertRaises(CartoException, msg=err_msg):
            dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_append(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        dataset = Dataset.from_dataframe(df).upload(
            if_exists=Dataset.APPEND, table_name=self.test_write_table, context=self.cc)

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049 * 2)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_dataset_write_if_exists_replace(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset.from_dataframe(df).upload(table_name=self.test_write_table, context=self.cc)
        self.test_write_table = dataset.table_name

        dataset = Dataset.from_dataframe(df).upload(
            if_exists=Dataset.REPLACE, table_name=self.test_write_table, context=self.cc)

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    def test_dataset_schema_from_parameter(self):
        schema = 'fake_schema'
        dataset = Dataset.from_table(table_name='fake_table', schema=schema, context=self.cc)
        self.assertEqual(dataset.schema, schema)

    def test_dataset_schema_from_non_org_context(self):
        dataset = Dataset.from_table(table_name='fake_table', context=self.cc)
        self.assertEqual(dataset.schema, 'public')

    def test_dataset_schema_from_org_context(self):
        username = 'fake_username'

        class FakeCreds():
            def username(self):
                return username

        class FakeContext():
            def __init__(self):
                self.is_org = True
                self.creds = FakeCreds()

            def get_default_schema(self):
                return username

        dataset = Dataset.from_table(table_name='fake_table', context=FakeContext())
        self.assertEqual(dataset.schema, username)

    def test_decode_geom(self):
        # Point (0, 0) without SRID
        ewkb = '010100000000000000000000000000000000000000'
        decoded_geom = _decode_geom(ewkb)
        self.assertEqual(decoded_geom.wkt, 'POINT (0 0)')
        self.assertIsNone(_decode_geom(None))

    # FIXME does not work in python 2.7 (COPY stucks and blocks the table, fix after
    # https://github.com/CartoDB/CartoDB-SQL-API/issues/579 is fixed)
    # @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    # def test_dataset_write_with_encoding(self):
    #     df = pd.DataFrame({'vals': [1, 2], 'strings': ['a', 'ô']})
    #     dataset = self.cc.write(df, self.test_write_table)
    #     self.test_write_table = dataset.table_name

    #     self.assertExistsTable(self.test_write_table)

    def assertExistsTable(self, table_name):
        resp = self.cc.sql_client.send('''
            SELECT *
            FROM {table}
            LIMIT 0
            '''.format(table=table_name))
        self.assertIsNotNone(resp)

    def assertNotExistsTable(self, table_name):
        try:
            self.cc.sql_client.send('''
                SELECT *
                FROM {table}
                LIMIT 0
                '''.format(table=table_name))
        except CartoException as e:
            self.assertTrue('relation "{}" does not exist'.format(table_name) in str(e))

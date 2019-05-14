# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.context"""
import unittest
import os
import sys
import json
import warnings

from carto.exceptions import CartoException

from cartoframes.context import CartoContext
from cartoframes.dataset import Dataset
from cartoframes.columns import normalize_name

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

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_points_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_mcdonalds_nyc
        df = read_mcdonalds_nyc(limit=100)
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_lines_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_ne_50m_graticules_15
        df = read_ne_50m_graticules_15()
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 35)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_polygons_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_lnglat_dataset(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        dataset = Dataset(self.cc, self.test_write_table, df=df) \
            .upload(with_lonlat=('dropoff_longitude', 'dropoff_latitude'))
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_null_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=100)
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 100)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_with_different_geometry_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        df.rename(columns={'the_geom': 'geometry'}, inplace=True)
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_with_different_geom_column(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()

        df.rename(columns={'the_geom': 'geom'}, inplace=True)
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_geopandas(self):
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

        dataset = Dataset(self.cc, self.test_write_table, df=gdf).upload()
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_wkt(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_taxi
        df = read_taxi(limit=50)
        df['the_geom'] = df.apply(lambda x: 'POINT ({x} {y})'
                                  .format(x=x['dropoff_longitude'], y=x['dropoff_latitude']), axis=1)
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 50)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_if_exists_fail_by_default(self):
        self.assertNotExistsTable(self.test_write_table)

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        with self.assertRaises(NameError):
            dataset = Dataset(self.cc, self.test_write_table, df=df).upload()

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_if_exists_append(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        dataset = Dataset(self.cc, self.test_write_table, df=df).upload(if_exists=Dataset.APPEND)

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049 * 2)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write_if_exists_replace(self):
        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()
        dataset = Dataset(self.cc, self.test_write_table, df=df).upload()
        self.test_write_table = dataset.table_name

        dataset = Dataset(self.cc, self.test_write_table, df=df).upload(if_exists=Dataset.REPLACE)

        self.assertExistsTable(self.test_write_table)

        result = self.cc.sql_client.send('SELECT * FROM {} WHERE the_geom IS NOT NULL'.format(self.test_write_table))
        self.assertEqual(result['total_rows'], 2049)

    # FIXME does not work in python 2.7 (COPY stucks and blocks the table, fix after
    # https://github.com/CartoDB/CartoDB-SQL-API/issues/579 is fixed)
    # @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    # def test_cartocontext_write_with_encoding(self):
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

# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.auth.context"""
try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
except RuntimeError:
    plt = None

import unittest
import os
import sys
import json
import random
import warnings
import requests
from datetime import datetime

from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
import pandas as pd

from cartoframes.data import Dataset
from cartoframes.utils import dict_items
from cartoframes.columns import normalize_name
from cartoframes.auth import Context, Credentials

from ..utils import _UserUrlLoader

WILL_SKIP = False
warnings.filterwarnings('ignore')


class TestContext(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.auth.Context"""

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

        self.user_url = self.user_url()

        if self.username and self.apikey:
            self.baseurl = self.user_url.format(username=self.username)
            self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                                api_key=self.apikey)
            self.sql_client = SQLClient(self.auth_client)

        # sets skip value
        WILL_SKIP = self.apikey is None or self.username is None  # noqa: F841

        # table naming info
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        has_gpd = 'gpd' if os.environ.get('USE_GEOPANDAS') else 'nongpd'
        pyver = sys.version[0:3].replace('.', '_')
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER')

        test_slug = '{ver}_{num}_{mpl}_{gpd}'.format(
            ver=pyver, num=buildnum, mpl=has_mpl, gpd=has_gpd
        )

        # test tables
        self.test_read_table = 'cb_2013_us_csa_500k'
        self.valid_columns = set(['affgeoid', 'aland', 'awater', 'created_at',
                                  'csafp', 'geoid', 'lsad', 'name', 'the_geom',
                                  'updated_at'])
        # torque table
        self.test_point_table = 'tweets_obama'

        # for writing to carto
        self.test_write_table = normalize_name(
            'cf_test_table_{}'.format(test_slug)
        )

        self.mixed_case_table = normalize_name(
            'AbCdEfG_{}'.format(test_slug)
        )

        # for batch writing to carto
        self.test_write_batch_table = normalize_name(
            'cf_testbatch_table_{}'.format(test_slug)
        )

        self.test_write_lnglat_table = normalize_name(
            'cf_testwrite_lnglat_table_{}'.format(test_slug)
        )

        self.write_named_index = normalize_name(
            'cf_testwrite_non_default_index_{}'.format(test_slug)
        )

        # for queries
        self.test_query_table = normalize_name(
            'cf_testquery_table_{}'.format(test_slug)
        )

        self.test_delete_table = normalize_name(
            'cf_testdelete_table_{}'.format(test_slug)
        )

        # for data observatory
        self.test_data_table = 'carto_usa_offices'

    def tearDown(self):
        """restore to original state"""
        tables = (self.test_write_table,
                  self.test_write_batch_table,
                  self.test_write_lnglat_table,
                  self.test_query_table,
                  self.mixed_case_table.lower(),
                  self.write_named_index, )
        sql_drop = 'DROP TABLE IF EXISTS {};'

        if self.apikey and self.baseurl:
            con = Context(base_url=self.baseurl,
                          api_key=self.apikey)
            for table in tables:
                try:
                    con.delete(table)
                    con.sql_client.send(sql_drop.format(table))
                except CartoException:
                    warnings.warn('Error deleting tables')

    @unittest.skipIf(WILL_SKIP, 'Skipping test, no carto credentials found')
    def test_Context(self):
        """Context.__init__ normal usage"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        self.assertEqual(con.creds.api_key, self.apikey)
        self.assertEqual(con.creds.base_url, self.baseurl.strip('/'))
        self.assertEqual(con.creds.username, self.username)
        self.assertTrue(not con.is_org)
        with self.assertRaises(CartoException):
            Context(base_url=self.baseurl,
                    api_key='notavalidkey')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_credentials(self):
        """Context.__init__ Credentials argument"""
        creds = Credentials(base_url=self.baseurl,
                            username=self.username,
                            api_key=self.apikey)
        con = Context(creds=creds)
        self.assertIsInstance(con, Context)
        self.assertEqual(con.creds.username, self.username)
        self.assertEqual(con.creds.api_key, self.apikey)

        # NOTE: this behaviour is not supported by "new" Credentials
        # Context pulls from saved credentials
        # saved_creds = Credentials(base_url=self.baseurl,
        #                           username=self.username,
        #                           api_key=self.apikey)
        # saved_creds.save()
        # c_saved = Context()
        # self.assertEqual(c_saved.creds.api_key, self.apikey)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_authenticated(self):
        """Context._is_authenticated"""
        with self.assertRaises(ValueError):
            Context(
                base_url=self.baseurl.replace('https', 'http'),
                api_key=self.apikey
            )

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_isorguser(self):
        """Context._is_org_user"""
        con = Context(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        self.assertTrue(not con._is_org_user())

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_read(self):
        """Context.read"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        # fails if limit is smaller than zero
        with self.assertRaises(ValueError):
            df = con.read(self.test_read_table, limit=-10)
        # fails if not an int
        with self.assertRaises(ValueError):
            df = con.read(self.test_read_table, limit=3.14159)
        with self.assertRaises(ValueError):
            df = con.read(self.test_read_table, limit='acadia')

        # fails on non-existent table
        with self.assertRaises(CartoException):
            df = con.read('non_existent_table')

        # normal table
        df = con.read(self.test_read_table)
        self.assertSetEqual(set(df.columns), self.valid_columns)
        self.assertTrue(len(df) == 169)

        # read with limit
        df = con.read(self.test_read_table, limit=10)
        self.assertEqual(len(df), 10)
        self.assertIsInstance(df, pd.DataFrame)

        # read empty table/dataframe
        df = con.read(self.test_read_table, limit=0)
        self.assertSetEqual(set(df.columns), self.valid_columns)
        self.assertEqual(len(df), 0)
        self.assertIsInstance(df, pd.DataFrame)

    def test_Context_read_with_same_schema(self):
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        df = pd.DataFrame({'fips': ['01'],
                           'cfips': ['0001'],
                           'intval': [1],
                           'floatval': [1.0],
                           'boolval': [True],
                           'textval': ['text'],
                           'dateval': datetime.now()
                           })
        df['boolval'] = df['boolval'].astype(bool)
        con.write(df, self.test_write_table, overwrite=True)
        read_df = con.read(self.test_write_table)

        read_df.drop('the_geom', axis=1, inplace=True)
        self.assertSetEqual(set(df.columns), set(read_df.columns))
        self.assertTupleEqual(
            tuple('float64' if str(d) == 'int64' else str(d) for d in df.dtypes),
            tuple(str(d) for d in read_df.dtypes),
            msg='Should have same schema/types'
        )
        self.assertEqual(read_df.index.name, 'cartodb_id')
        self.assertEqual(read_df.index.dtype, 'int64')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_write(self):
        """Context.write normal usage"""
        con = Context(base_url=self.baseurl,
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
        dataset = con.write(df, self.test_write_table)
        self.test_write_table = dataset.table_name

        # check if table exists
        resp = self.sql_client.send('''
            SELECT *
            FROM {table}
            LIMIT 0
            '''.format(table=self.test_write_table))
        self.assertIsNotNone(resp)

        # check that table has same number of rows
        resp = self.sql_client.send('''
            SELECT count(*)
            FROM {table}'''.format(table=self.test_write_table))
        self.assertEqual(resp['rows'][0]['count'], len(df))

        # should error for existing table
        err_msg = ('Table with name {t} and schema {s} already exists in CARTO. Please choose a different `table_name`'
                   'or use if_exists="replace" to overwrite it').format(t=self.test_write_table, s='public')
        with self.assertRaises(CartoException, msg=err_msg):
            con.write(df, self.test_read_table, overwrite=False)

        # overwrite table and create the_geom column
        con.write(df, self.test_write_table,
                  overwrite=True,
                  lnglat=('long', 'lat'))

        resp = self.sql_client.send('''
            SELECT count(*) AS num_rows, count(the_geom) AS num_geoms
            FROM {table}
            '''.format(table=self.test_write_table))
        # number of geoms should equal number of rows
        self.assertEqual(resp['rows'][0]['num_rows'],
                         resp['rows'][0]['num_geoms'])

        con.delete(self.test_write_table)
        df = pd.DataFrame({'vals': list('abcd'), 'ids': list('wxyz')})
        df = df.astype({'vals': str, 'ids': str})
        con.write(df, self.test_write_table, overwrite=True)
        schema = con.sql_client.send('select ids, vals from {}'.format(
            self.test_write_table))['fields']
        self.assertSetEqual(set([schema[s]['type'] for s in schema]),
                            set(('string', )))

        df = pd.DataFrame({'vals': list('abcd'),
                           'ids': list('wxyz'),
                           'nums': [1.2 * i for i in range(4)],
                           'boolvals': [True, False, None, True, ],
                           })
        df['boolvals'] = df['boolvals'].astype(bool)
        con.write(df, self.test_write_table, overwrite=True)
        resp = con.sql_client.send('SELECT * FROM {}'.format(
            self.test_write_table))['fields']
        schema = {k: v['type'] for k, v in dict_items(resp)}
        ans = dict(vals='string', ids='string', nums='number',
                   boolvals='boolean', the_geom='geometry',
                   the_geom_webmercator='geometry', cartodb_id='number')
        self.assertDictEqual(schema, ans)

    # FIXME in https://github.com/CartoDB/cartoframes/issues/579
    # @unittest.skipIf(WILL_SKIP, 'updates privacy of existing dataset')
    # def test_write_privacy(self):
    #     """Context.write Updates the privacy of a dataset"""
    #     from carto.datasets import DatasetManager
    #     con = Context(base_url=self.baseurl,
    #                                   api_key=self.apikey)
    #     ds_manager = DatasetManager(self.auth_client)

    #     df = pd.DataFrame({'ids': list('abcd'), 'vals': range(4)})
    #     dataset = con.write(df, self.test_write_table)
    #     self.test_write_table = dataset.table_name
    #     dataset = ds_manager.get(self.test_write_table)
    #     self.assertEqual(dataset.privacy.lower(), 'private')

    #     df = pd.DataFrame({'ids': list('efgh'), 'vals': range(4, 8)})
    #     con.write(df, self.test_write_table, overwrite=True, privacy='public')
    #     dataset = ds_manager.get(self.test_write_table)
    #     self.assertEqual(dataset.privacy.lower(), 'public')

    #     privacy = con._get_privacy('i_am_not_a_table_in_this_account')
    #     self.assertIsNone(privacy)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_write_index(self):
        """Context.write with non-default index"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        df = pd.DataFrame({'vals': range(3), 'ids': list('abc')},
                          index=list('xyz'))
        df.index.name = 'named_index'
        dataset = con.write(df, self.write_named_index)
        self.write_named_index = dataset.table_name

        df_index = con.read(self.write_named_index)
        self.assertSetEqual(set(('the_geom', 'vals', 'ids', 'named_index')),
                            set(df_index.columns))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_mixed_case(self):
        """Context.write table name mixed case"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        data = pd.DataFrame({'a': [1, 2, 3],
                             'B': list('abc')})
        con.write(pd.DataFrame(data), self.mixed_case_table, overwrite=True)

    def test_Context_delete(self):
        """Context.delete"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        data = {'col1': [1, 2, 3],
                'col2': ['a', 'b', 'c']}
        df = pd.DataFrame(data)

        dataset = con.write(df, self.test_delete_table, overwrite=True)
        self.test_delete_table = dataset.table_name
        con.delete(self.test_delete_table)

        # check that querying recently deleted table raises an exception
        with self.assertRaises(CartoException):
            con.sql_client.send('select * from {}'.format(
                self.test_delete_table))

    def test_Context_delete_non_existent_table(self):
        """Context.delete"""
        con = Context(base_url=self.baseurl, api_key=self.apikey)
        table_name = 'non_existent_table'

        with self.assertRaises(
                CartoException,
                msg='''The table `{}` doesn't exist'''.format(table_name)):
            con.delete(table_name)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_get_bounds(self):
        """Context._get_bounds"""
        from cartoframes.layer import QueryLayer
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        vals1 = {'minx': 0,
                 'maxx': 1,
                 'miny': 0,
                 'maxy': 2}

        vals2 = {'minx': 0,
                 'maxx': 1.5,
                 'miny': -0.5,
                 'maxy': 1.5}
        ans = {'west': 0,
               'east': 1.5,
               'south': -0.5,
               'north': 2}
        # (MINX, MINY), (MINX, MAXY), (MAXX, MAXY), (MAXX, MINY), (MINX, MINY)
        # https://postgis.net/docs/ST_Envelope.html
        query = '''
            WITH cte AS (
                SELECT
                  'SRID=4326;POLYGON(({minx} {miny},
                                      {minx} {maxy},
                                      {maxx} {maxy},
                                      {maxx} {miny},
                                      {minx} {miny}))'::geometry AS the_geom
              )
            SELECT
              1 AS cartodb_id,
              the_geom,
              ST_Transform(the_geom, 3857) AS the_geom_webmercator
            FROM cte
        '''
        layers = [QueryLayer(query.format(**vals1)),
                  QueryLayer(query.format(**vals2))]
        extent_ans = con._get_bounds(layers)

        self.assertDictEqual(extent_ans, ans)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_check_query(self):
        """Context._check_query"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        # this table does not exist in this account
        fail_query = '''
            SELECT *
              FROM cyclists
              '''
        fail_cols = ['merckx', 'moser', 'gimondi']
        with self.assertRaises(ValueError):
            con._check_query(fail_query, style_cols=fail_cols)

        # table exists
        success_query = '''
            SELECT *
              FROM {}
              '''.format(self.test_read_table)
        self.assertIsNone(con._check_query(success_query))

        # table exists but columns don't
        with self.assertRaises(ValueError):
            con._check_query(success_query, style_cols=fail_cols)

    def test_debug_print(self):
        """_debug_print"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey,
                      verbose=True)
        # request-response usage
        resp = requests.get('http://httpbin.org/get')
        con._debug_print(resp=resp)
        con._debug_print(resp=resp.text)

        # non-requests-response usage
        test_str = 'this is a test'
        long_test_str = ', '.join([test_str] * 100)
        self.assertIsNone(con._debug_print(test_str=test_str))
        self.assertIsNone(con._debug_print(long_str=long_test_str))

        # verbose = False test
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey,
                      verbose=False)
        self.assertIsNone(con._debug_print(resp=test_str))

    def test_tables(self):
        """Context.tables normal usage"""
        con = Context(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        datasets = con.tables()
        self.assertIsInstance(datasets, list)
        self.assertIsInstance(datasets[0], Dataset)
        self.assertIsNotNone(datasets[0].table_name)
        self.assertIsInstance(datasets[0].table_name, str)

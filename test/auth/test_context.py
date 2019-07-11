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
import IPython

import cartoframes
from cartoframes.data import Dataset
from cartoframes.utils import dict_items
from cartoframes.columns import Column, normalize_name
from cartoframes.auth import Context, Credentials

from utils import _UserUrlLoader

WILL_SKIP = False
warnings.filterwarnings("ignore")


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

        # TODO: remove the named map templates

    def add_map_template(self):
        """Add generated named map templates to class"""
        pass

    @unittest.skipIf(WILL_SKIP, 'Skipping test, no carto credentials found')
    def test_Context(self):
        """Context.__init__ normal usage"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        self.assertEqual(con.creds.key(), self.apikey)
        self.assertEqual(con.creds.base_url(), self.baseurl.strip('/'))
        self.assertEqual(con.creds.username(), self.username)
        self.assertTrue(not con.is_org)
        with self.assertRaises(CartoException):
            Context(base_url=self.baseurl,
                    api_key='notavalidkey')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_credentials(self):
        """Context.__init__ Credentials argument"""
        creds = Credentials(base_url=self.baseurl,
                            username=self.username,
                            key=self.apikey)
        con = Context(creds=creds)
        self.assertIsInstance(con, Context)
        self.assertEqual(con.creds.username(), self.username)
        self.assertEqual(con.creds.key(), self.apikey)

        # Context pulls from saved credentials
        saved_creds = Credentials(base_url=self.baseurl,
                                  username=self.username,
                                  key=self.apikey)
        saved_creds.save()
        c_saved = Context()
        self.assertEqual(c_saved.creds.key(), self.apikey)

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
    def test_cartoframes_sync(self):
        """Context.sync"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        self.assertIsNone(con.sync(pd.DataFrame(), 'acadia'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_query(self):
        """Context.query"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        columns = (Column('link', pgtype='string'),
                   Column('body', pgtype='string'),
                   Column('displayname', pgtype='string'),
                   Column('friendscount', pgtype='number'),
                   Column('postedtime', pgtype='date'), )
        cols = [col.name for col in columns]
        df = con.query('''
            SELECT {cols}, '02-06-1429'::date as invalid_df_date
            FROM tweets_obama
            LIMIT 100
            '''.format(cols=','.join(cols)))

        # ensure columns are in expected order
        df = df[list(cols) + ['invalid_df_date', ]]

        # same number of rows
        self.assertEqual(len(df), 100,
                         msg='Expected number or rows')

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        requested_cols = {'link', 'body', 'displayname', 'friendscount',
                          'postedtime', 'invalid_df_date', }
        self.assertSetEqual(requested_cols,
                            set(df.columns),
                            msg='Should have the columns requested')

        # should have exected schema
        expected_dtypes = ('object', 'object', 'object', 'float64',
                           'datetime64[ns, UTC]', 'object', )
        self.assertTupleEqual(
            tuple(str(d) for d in df.dtypes),
            expected_dtypes,
            msg='Should have same schema/types'
        )

        # empty response
        df_empty = con.query('''
            SELECT 1
            LIMIT 0
            ''')

        # no rows, one column
        self.assertTupleEqual(df_empty.shape, (0, 1))

        # is a DataFrame
        self.assertIsInstance(df_empty, pd.DataFrame)

        # table already exists, should throw CartoException
        with self.assertRaises(CartoException):
            con.query('''
                SELECT link, body, displayname, friendscount
                FROM tweets_obama
                LIMIT 100
                ''', table_name='tweets_obama')

        # create a table from a query
        con.query('''
            SELECT link, body, displayname, friendscount
            FROM tweets_obama
            LIMIT 100
            ''', table_name=self.test_query_table)

        # read newly created table into a dataframe
        df = con.read(self.test_query_table)
        # should be specified length
        self.assertEqual(len(df), 100)
        # should have requested columns + utility columns from CARTO
        self.assertSetEqual({'body', 'displayname', 'link', 'friendscount',
                             'the_geom', },
                            set(df.columns),
                            msg='Should have the columns requested')

        # see what happens if a query fails after 100 successful rows
        with self.assertRaises(CartoException):
            con.query('''
                WITH cte AS (
                    SELECT CDB_LatLng(0, 0) as the_geom, i
                    FROM generate_series(1, 110) as m(i)
                    UNION ALL
                    SELECT ST_Buffer(CDB_LatLng(0, 0), 0.1) as the_geom, i
                    FROM generate_series(111, 120) as i
                )
                SELECT ST_X(the_geom) as xval, ST_Y(the_geom) as yval
                FROM cte
            ''', is_select=True)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_fetch(self):
        """Context.fetch"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        columns = (Column('link', pgtype='string'),
                   Column('body', pgtype='string'),
                   Column('displayname', pgtype='string'),
                   Column('friendscount', pgtype='number'),
                   Column('postedtime', pgtype='date'), )
        cols = [col.name for col in columns]
        df = con.fetch('''
            SELECT {cols}, '02-06-1429'::date as invalid_df_date
            FROM tweets_obama
            LIMIT 100
            '''.format(cols=','.join(cols)))

        # ensure columns are in expected order
        df = df[list(cols) + ['invalid_df_date', ]]

        # same number of rows
        self.assertEqual(len(df), 100,
                         msg='Expected number or rows')

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        requested_cols = {'link', 'body', 'displayname', 'friendscount',
                          'postedtime', 'invalid_df_date', }
        self.assertSetEqual(requested_cols,
                            set(df.columns),
                            msg='Should have the columns requested')

        # should have exected schema
        expected_dtypes = ('object', 'object', 'object', 'float64',
                           'datetime64[ns, UTC]', 'object', )
        self.assertTupleEqual(
            tuple(str(d) for d in df.dtypes),
            expected_dtypes,
            msg='Should have same schema/types'
        )

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_fetch_empty(self):
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        # empty response
        df_empty = con.fetch('''
            SELECT 1
            LIMIT 0
            ''')

        # no rows, one column
        self.assertTupleEqual(df_empty.shape, (0, 1))

        # is a DataFrame
        self.assertIsInstance(df_empty, pd.DataFrame)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_fetch_with_cte(self):
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        df = con.fetch('''
            WITH cte AS (
                SELECT CDB_LatLng(0.1, 0) as the_geom, i
                FROM generate_series(1, 110) as m(i)
            )
            SELECT ST_X(the_geom) as xval, ST_Y(the_geom) as yval
            FROM cte
        ''')

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        requested_cols = {'xval', 'yval'}
        self.assertSetEqual(requested_cols,
                            set(df.columns),
                            msg='Should have the columns requested')

        # should have exected schema
        expected_dtypes = ('float64', 'float64')
        self.assertTupleEqual(
            tuple(str(d) for d in df.dtypes),
            expected_dtypes,
            msg='Should have same schema/types'
        )

        # same number of rows
        self.assertEqual(len(df), 110,
                         msg='Expected number or rows')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_fetch_with_decode_geom(self):
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        df = con.fetch('''
            SELECT CDB_LatLng(0.1, 0) as the_geom, i
            FROM generate_series(1, 110) as m(i)
        ''', decode_geom=True)

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')

        # same column names
        requested_cols = {'geometry', 'i'}
        self.assertSetEqual(requested_cols,
                            set(df.columns),
                            msg='Should have the columns requested')

        # should have exected schema
        expected_dtypes = ('object', 'float64')
        self.assertTupleEqual(
            tuple(str(d) for d in df.dtypes),
            expected_dtypes,
            msg='Should have same schema/types'
        )

        # same number of rows
        self.assertEqual(len(df), 110,
                         msg='Expected number or rows')

        self.assertEqual(df.loc[0].geometry.wkt, 'POINT (0 0.1)')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_fetch_with_exception(self):
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        # see what happens if a query fails after 100 successful rows
        with self.assertRaises(CartoException):
            con.fetch('''
                WITH cte AS (
                    SELECT CDB_LatLng(0, 0) as the_geom, i
                    FROM generate_series(1, 110) as m(i)
                    UNION ALL
                    SELECT ST_Buffer(CDB_LatLng(0, 0), 0.1) as the_geom, i
                    FROM generate_series(111, 120) as i
                )
                SELECT ST_X(the_geom) as xval, ST_Y(the_geom) as yval
                FROM cte
            ''')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_execute(self):
        """Context.execute"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        df = pd.DataFrame({'vals': list('abcd'), 'ids': list('wxyz')})
        df = df.astype({'vals': str, 'ids': str})
        con.write(df, self.test_write_table, overwrite=True)

        self.assertEquals(Dataset(self.test_write_table, context=con).exists(), True)

        con.execute('''
            DROP TABLE {table_name}
            '''.format(table_name=self.test_write_table))

        self.assertEquals(Dataset(self.test_write_table, context=con).exists(), False)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_Context_execute_wrong_query(self):
        """Context.execute"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        with self.assertRaises(CartoException):
            con.execute('''
                DROPP TABLE {table_name}
                '''.format(table_name=self.test_write_table))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_map(self):
        """Context.map normal usage"""
        from cartoframes import Layer, QueryLayer, BaseMap
        con = Context(base_url=self.baseurl, api_key=self.apikey)

        # test with no layers - should produce basemap
        if plt:
            basemap_only_static_mpl = con.map(interactive=False)
            cartoframes.auth.context.HAS_MATPLOTLIB = False
        basemap_only_static = con.map(interactive=False)
        basemap_only_interactive = con.map(interactive=True)

        # are of the correct type instances
        if plt:
            self.assertIsInstance(basemap_only_static_mpl,
                                  plt.Axes)
        self.assertIsInstance(basemap_only_static,
                              IPython.core.display.Image)
        self.assertIsInstance(basemap_only_interactive,
                              IPython.core.display.HTML)

        # have the HTML innards that are to be expected
        if sys.version[0] == 3:
            self.assertRegex(basemap_only_static.data,
                             ('^<img src="https://.*api/v1/map/static/named/'
                              'cartoframes_ver.*" />$'))
            self.assertRegex(basemap_only_interactive.data,
                             '^<iframe srcdoc="<!DOCTYPE html>.*')
        elif sys.version[0] == 2:
            self.assertRegexMatches(
                basemap_only_static.data,
                ('^<img src="https://.*api/v1/map/static/named/'
                 'cartoframes_ver.*" />$'))
            self.assertRegexMatches(
                basemap_only_interactive.data,
                '^<iframe srcdoc="<!DOCTYPE html>.*')

        # test with labels on front
        labels_front = con.map(layers=BaseMap('light', labels='front'))
        self.assertIsInstance(labels_front, IPython.core.display.HTML)

        # test with one Layer
        one_layer = con.map(layers=Layer('tweets_obama'))
        self.assertIsInstance(one_layer, IPython.core.display.HTML)

        # test with two Layers
        two_layers = con.map(layers=[Layer('tweets_obama'),
                                     Layer(self.test_read_table)])

        self.assertIsInstance(two_layers, IPython.core.display.HTML)

        # test with one Layer, one QueryLayer
        onelayer_onequery = con.map(layers=[QueryLayer('''
                                                SELECT *
                                                FROM tweets_obama
                                                LIMIT 100'''),
                                            Layer(self.test_read_table)])

        self.assertIsInstance(onelayer_onequery, IPython.core.display.HTML)

        # test with BaseMap, Layer, QueryLayer
        con.map(layers=[BaseMap('light'),
                        QueryLayer('''
                               SELECT *
                               FROM tweets_obama
                               LIMIT 100''', color='favoritescount'),
                        Layer(self.test_read_table)])

        # Errors
        # too many layers
        with self.assertRaises(ValueError):
            layers = [Layer('tweets_obama')] * 9
            con.map(layers=layers)

        # zoom needs to be specified with lng/lat
        with self.assertRaises(ValueError):
            con.map(lng=44.3386, lat=68.2733)

        # only one basemap layer can be added
        with self.assertRaises(ValueError):
            con.map(layers=[BaseMap('dark'), BaseMap('light')])

        # only one time layer can be added
        with self.assertRaises(ValueError):
            con.map(layers=[Layer(self.test_read_table, time='cartodb_id'),
                            Layer(self.test_read_table, time='cartodb_id')])

        # no geometry
        with self.assertRaises(ValueError):
            con.map(layers=QueryLayer('''
                SELECT
                    null::geometry as the_geom,
                    null::geometry as the_geom_webmercator,
                    row_number() OVER () as cartodb_id
                FROM generate_series(1, 10) as m(i)
                '''))

    @unittest.skipIf(WILL_SKIP, 'no cartocredentials, skipping')
    def test_Context_map_time(self):
        """Context.map time options"""
        from cartoframes import Layer
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        html_map = con.map(layers=Layer(self.test_point_table,
                                        time='cartodb_id'))
        self.assertIsInstance(html_map, IPython.core.display.HTML)

        # category map
        cat_map = con.map(layers=Layer(self.test_point_table,
                                       time='actor_postedtime',
                                       color='twitter_lang'))
        self.assertRegexpMatches(cat_map.__html__(), '.*CDB_Math_Mode\(cf_value_twitter_lang\).*')

        with self.assertRaises(
                ValueError,
                msg='cannot create static torque maps currently'):
            con.map(layers=Layer(self.test_point_table, time='cartodb_id'),
                    interactive=False)

        with self.assertRaises(
                ValueError,
                msg='cannot have more than one torque layer'):
            con.map(layers=[Layer(self.test_point_table, time='cartodb_id'),
                            Layer(self.test_point_table, color='cartodb_id')])

        with self.assertRaises(
                ValueError,
                msg='cannot do a torque map off a polygon dataset'):
            con.map(layers=Layer(self.test_read_table, time='cartodb_id'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_Context_map_geom_type(self):
        """Context.map basemap geometry type defaults"""
        from cartoframes import Layer, QueryLayer
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        # baseid1 = dark, labels1 = labels on top in named map name
        labels_polygon = con.map(layers=Layer(self.test_read_table))
        self.assertRegexpMatches(labels_polygon.__html__(),
                                 '.*baseid2_labels1.*',
                                 msg='labels should be on top since only a '
                                     'polygon layer is present')

        # baseid2 = voyager, labels0 = labels on bottom
        labels_point = con.map(layers=Layer(self.test_point_table))
        self.assertRegexpMatches(labels_point.__html__(),
                                 '.*baseid2_labels0.*',
                                 msg='labels should be on bottom because a '
                                     'point layer is present')

        labels_multi = con.map(layers=[Layer(self.test_point_table),
                                       Layer(self.test_read_table)])
        self.assertRegexpMatches(labels_multi.__html__(),
                                 '.*baseid2_labels0.*',
                                 msg='labels should be on bottom because a '
                                     'point layer is present')
        # create a layer with points and polys, but with more polys
        # should default to poly layer (labels on top)
        multi_geom_layer = QueryLayer('''
            (SELECT
                the_geom, the_geom_webmercator,
                row_number() OVER () AS cartodb_id
              FROM "{polys}" WHERE the_geom IS NOT null LIMIT 10)
            UNION ALL
            (SELECT
                the_geom, the_geom_webmercator,
                (row_number() OVER ()) + 10 AS cartodb_id
              FROM "{points}" WHERE the_geom IS NOT null LIMIT 5)
        '''.format(polys=self.test_read_table,
                   points=self.test_point_table))
        multi_geom = con.map(layers=multi_geom_layer)
        self.assertRegexpMatches(multi_geom.__html__(),
                                 '.*baseid2_labels1.*',
                                 msg='layer has more polys than points, so it '
                                     'should default to polys labels (on top)')

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

    def test_data_boundaries(self):
        """Context.data_boundaries"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        # all boundary metadata
        boundary_meta = con.data_boundaries()
        self.assertTrue(boundary_meta.shape[0] > 0,
                        msg='has non-zero number of boundaries')
        meta_cols = set(('geom_id', 'geom_tags', 'geom_type', ))
        self.assertTrue(meta_cols & set(boundary_meta.columns))

        # boundary metadata with correct timespan
        meta_2015 = con.data_boundaries(timespan='2015')
        self.assertTrue(meta_2015[meta_2015.valid_timespan].shape[0] > 0)

        # test for no data with an incorrect or invalid timespan
        meta_9999 = con.data_boundaries(timespan='invalid_timespan')
        self.assertTrue(meta_9999[meta_9999.valid_timespan].shape[0] == 0)

        # boundary metadata in a region
        regions = (
            self.test_read_table,
            self.test_data_table,
            [5.9559111595, 45.8179931641, 10.4920501709, 47.808380127],
            'Australia', )
        for region in regions:
            boundary_meta = con.data_boundaries(region=region)
            self.assertTrue(meta_cols & set(boundary_meta.columns))
            self.assertTrue(boundary_meta.shape[0] > 0,
                            msg='has non-zero number of boundaries')

        #  boundaries for world
        boundaries = con.data_boundaries(boundary='us.census.tiger.state')
        self.assertTrue(boundaries.shape[0] > 0)
        self.assertEqual(boundaries.shape[1], 2)
        self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                            set(boundaries.columns))

        # boundaries for region
        boundaries = ('us.census.tiger.state', )
        for b in boundaries:
            geoms = con.data_boundaries(
                boundary=b,
                region=self.test_data_table)
            self.assertTrue(geoms.shape[0] > 0)
            self.assertEqual(geoms.shape[1], 2)
            self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                                set(geoms.columns))

        # presence or lack of clipped boundaries
        nonclipped = (True, False, )
        for tf in nonclipped:
            meta = con.data_boundaries(include_nonclipped=tf)
            self.assertEqual(
                'us.census.tiger.state' in set(meta.geom_id),
                tf
            )

        with self.assertRaises(ValueError):
            con.data_boundaries(region=[1, 2, 3])

        with self.assertRaises(ValueError):
            con.data_boundaries(region=10)

    def test_data_discovery(self):
        """Context.data_discovery"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        meta = con.data_discovery(self.test_read_table,
                                  keywords=('poverty', ),
                                  time=('2010 - 2014', ))
        meta_columns = set((
            'denom_aggregate', 'denom_colname', 'denom_description',
            'denom_geomref_colname', 'denom_id', 'denom_name',
            'denom_reltype', 'denom_t_description', 'denom_tablename',
            'denom_type', 'geom_colname', 'geom_description',
            'geom_geomref_colname', 'geom_id', 'geom_name',
            'geom_t_description', 'geom_tablename', 'geom_timespan',
            'geom_type', 'id', 'max_score_rank', 'max_timespan_rank',
            'normalization', 'num_geoms', 'numer_aggregate',
            'numer_colname', 'numer_description', 'numer_geomref_colname',
            'numer_id', 'numer_name', 'numer_t_description',
            'numer_tablename', 'numer_timespan', 'numer_type', 'score',
            'score_rank', 'score_rownum', 'suggested_name', 'target_area',
            'target_geoms', 'timespan_rank', 'timespan_rownum'))
        self.assertSetEqual(set(meta.columns), meta_columns,
                            msg='metadata columns are all there')
        self.assertTrue((meta['numer_timespan'] == '2010 - 2014').all())
        self.assertTrue((meta['numer_description'].str.contains('poverty')).all())

        # test region = list of lng/lats
        with self.assertRaises(ValueError):
            con.data_discovery([1, 2, 3])

        switzerland = [5.9559111595, 45.8179931641,
                       10.4920501709, 47.808380127]
        dd = con.data_discovery(switzerland, keywords='freight', time='2010')
        self.assertEqual(dd['numer_id'][0], 'eu.eurostat.tgs00078')

        dd = con.data_discovery('Australia',
                                regex='.*Torres Strait Islander.*')
        for nid in dd['numer_id'].values:
            self.assertRegexpMatches(nid, '^au\.data\.B01_Indig_[A-Za-z_]+Torres_St[A-Za-z_]+[FMP]$')

        with self.assertRaises(CartoException):
            con.data_discovery('non_existent_table_abcdefg')

        dd = con.data_discovery('United States',
                                boundaries='us.epa.huc.hydro_unit',
                                time=('2006', '2010', ))
        self.assertTrue(dd.shape[0] >= 1)

        poverty = con.data_discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=False)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertEqual(df_quantiles.shape[0], 0)

        poverty = con.data_discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=True)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertTrue(df_quantiles.shape[0] > 0)

    def test_data(self):
        """Context.data"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        meta = con.data_discovery(self.test_read_table,
                                  keywords=('poverty', ),
                                  time=('2010 - 2014', ))
        data = con.data(self.test_data_table, meta)
        anscols = set(meta['suggested_name'])
        origcols = set(con.read(self.test_data_table, limit=1, decode_geom=True).columns)
        self.assertSetEqual(anscols, set(data.columns) - origcols - {'the_geom', 'cartodb_id'})

        meta = [{'numer_id': 'us.census.acs.B19013001',
                 'geom_id': 'us.census.tiger.block_group',
                 'numer_timespan': '2011 - 2015'}, ]
        data = con.data(self.test_data_table, meta)
        self.assertSetEqual(set(('median_income_2011_2015', )),
                            set(data.columns) - origcols - {'the_geom', 'cartodb_id'})

        with self.assertRaises(ValueError, msg='no measures'):
            meta = con.data_discovery('United States', keywords='not a measure')
            con.data(self.test_read_table, meta)

        with self.assertRaises(ValueError, msg='too many metadata measures'):
            # returns ~180 measures
            meta = con.data_discovery(region='united states',
                                      keywords='education')
            con.data(self.test_read_table, meta)

    def test_data_with_persist_as(self):
        """Context.data"""
        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)

        meta = con.data_discovery(self.test_read_table,
                                  keywords=('poverty', ),
                                  time=('2010 - 2014', ))
        data = con.data(self.test_data_table, meta)
        anscols = set(meta['suggested_name'])
        origcols = set(con.read(self.test_data_table, limit=1, decode_geom=True).columns)
        self.assertSetEqual(anscols, set(data.columns) - origcols - {'the_geom', 'cartodb_id'})

        meta = [{'numer_id': 'us.census.acs.B19013001',
                 'geom_id': 'us.census.tiger.block_group',
                 'numer_timespan': '2011 - 2015'}, ]
        data = con.data(self.test_data_table, meta, persist_as=self.test_write_table)
        self.assertSetEqual(set(('median_income_2011_2015', )),
                            set(data.columns) - origcols - {'the_geom', 'cartodb_id'})
        self.assertEqual(data.index.name, 'cartodb_id')
        self.assertEqual(data.index.dtype, 'int64')

        df = con.read(self.test_write_table, decode_geom=False)

        self.assertEqual(df.index.name, 'cartodb_id')
        self.assertEqual(data.index.dtype, 'int64')

        # same number of rows
        self.assertEqual(len(df), len(data),
                         msg='Expected number or rows')

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        self.assertSetEqual(set(data.columns.values),
                            set(df.columns.values),
                            msg='Should have the columns requested')

        # should have exected schema
        self.assertEqual(
            sorted(tuple(str(d) for d in df.dtypes)),
            sorted(tuple(str(d) for d in data.dtypes)),
            msg='Should have same schema/types'
        )

    def test_column_name_collision_do_enrichement(self):
        """Context.data column collision"""
        dup_col = 'female_third_level_studies_2011_by_female_pop'
        self.sql_client.send(
            """
            create table {table} as (
                select cdb_latlng(40.4165,-3.70256) the_geom,
                       1 {dup_col})
            """.format(
                dup_col=dup_col,
                table=self.test_write_table
            )
        )
        self.sql_client.send(
            "select cdb_cartodbfytable('public', '{table}')".format(
                table=self.test_write_table
            )
        )

        con = Context(base_url=self.baseurl,
                      api_key=self.apikey)
        meta = con.data_discovery(region=self.test_write_table,
                                  keywords='female')
        meta = meta[meta.suggested_name == dup_col]
        data = con.data(
            self.test_write_table,
            meta[meta.suggested_name == dup_col]
        )

        self.assertIn('_' + dup_col, data.keys())

    def test_tables(self):
        """Context.tables normal usage"""
        from cartoframes.analysis import Table
        con = Context(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        tables = con.tables()
        self.assertIsInstance(tables, list)
        self.assertIsInstance(tables[0], Table)
        self.assertIsNotNone(tables[0].name)
        self.assertIsInstance(tables[0].name, str)

# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.context"""
import unittest
import os
import sys
import json
import random
import warnings
import requests

import cartoframes
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
import pandas as pd
import IPython
from cartoframes.utils import dict_items

WILL_SKIP = False
warnings.filterwarnings("ignore")


class _UserUrlLoader:
    def user_url(self):
        user_url = None
        if (os.environ.get('USERURL') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                user_url = creds['USERURL']
            except:  # noqa: E722
                warnings.warn('secret.json not found')

        if user_url in (None, ''):
            user_url = 'https://{username}.carto.com/'

        return user_url


class TestCartoContext(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.CartoContext"""
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

        self.user_url = self.user_url()

        if self.username and self.apikey:
            self.baseurl = self.user_url.format(
                    username=self.username)
            self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                                api_key=self.apikey)
            self.sql_client = SQLClient(self.auth_client)

        # sets client to be ci
        if not cartoframes.context.DEFAULT_SQL_ARGS['client']\
                .endswith('_dev_ci'):
            cartoframes.context.DEFAULT_SQL_ARGS['client'] += '_dev_ci'
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
        table_args = dict(ver=pyver, mpl=has_mpl, gpd=has_gpd)
        # torque table
        self.test_point_table = 'tweets_obama'

        # for writing to carto
        self.test_write_table = (
            'cf_test_table_{}'
        ).format(test_slug)

        self.mixed_case_table = (
            'AbCdEfG_{}'
        ).format(test_slug)

        # for batch writing to carto
        self.test_write_batch_table = (
            'cf_testbatch_table_{}'
        ).format(test_slug)

        self.test_write_lnglat_table = (
            'cf_testwrite_lnglat_table_{}'
        ).format(test_slug)

        self.write_named_index = (
            'cf_testwrite_non_default_index_{}'
        ).format(test_slug)

        # for queries
        self.test_query_table = (
            'cf_testquery_table_{}'
        ).format(test_slug)

        self.test_delete_table = (
            'cf_testdelete_table_{}'
        ).format(test_slug)

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
            cc = cartoframes.CartoContext(base_url=self.baseurl,
                                          api_key=self.apikey)
            for table in tables:
                cc.delete(table)
                cc.sql_client.send(sql_drop.format(table))
        # TODO: remove the named map templates

    def add_map_template(self):
        """Add generated named map templates to class"""
        pass

    @unittest.skipIf(WILL_SKIP, 'Skipping test, no carto credentials found')
    def test_cartocontext(self):
        """context.CartoContext.__init__ normal usage"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertEqual(cc.creds.key(), self.apikey)
        self.assertEqual(cc.creds.base_url(), self.baseurl.strip('/'))
        self.assertEqual(cc.creds.username(), self.username)
        self.assertTrue(not cc.is_org)
        with self.assertRaises(CartoException):
            cartoframes.CartoContext(base_url=self.baseurl,
                                     api_key='notavalidkey')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_credentials(self):
        """context.CartoContext.__init__ Credentials argument"""
        creds = cartoframes.Credentials(base_url=self.baseurl,
                                        username=self.username,
                                        key=self.apikey)
        cc = cartoframes.CartoContext(creds=creds)
        self.assertIsInstance(cc, cartoframes.CartoContext)
        self.assertEqual(cc.creds.username(), self.username)
        self.assertEqual(cc.creds.key(), self.apikey)

        # CartoContext pulls from saved credentials
        saved_creds = cartoframes.Credentials(base_url=self.baseurl,
                                              username=self.username,
                                              key=self.apikey)
        saved_creds.save()
        cc_saved = cartoframes.CartoContext()
        self.assertEqual(cc_saved.creds.key(), self.apikey)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_authenticated(self):
        """context.CartoContext._is_authenticated"""
        with self.assertRaises(ValueError):
            cc = cartoframes.CartoContext(
                base_url=self.baseurl.replace('https', 'http'),
                api_key=self.apikey
            )

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_isorguser(self):
        """context.CartoContext._is_org_user"""
        cc = cartoframes.CartoContext(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        self.assertTrue(not cc._is_org_user())

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_read(self):
        """context.CartoContext.read"""
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
        self.assertSetEqual(set(df.columns), self.valid_columns)
        self.assertTrue(len(df) == 169)

        # read with limit
        df = cc.read(self.test_read_table, limit=10)
        self.assertEqual(len(df), 10)
        self.assertIsInstance(df, pd.DataFrame)

        # read empty table/dataframe
        df = cc.read(self.test_read_table, limit=0)
        self.assertSetEqual(set(df.columns), self.valid_columns)
        self.assertEqual(len(df), 0)
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write(self):
        """context.CartoContext.write normal usage"""
        from cartoframes.context import MAX_ROWS_LNGLAT
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
        self.assertIsNotNone(resp)

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

        # test batch lnglat behavior
        n_rows = MAX_ROWS_LNGLAT + 1
        df = pd.DataFrame({
            'latvals': [random.random() for r in range(n_rows)],
            'lngvals': [random.random() for r in range(n_rows)]
            })
        job = cc.write(df, self.test_write_lnglat_table,
                       lnglat=('lngvals', 'latvals'))
        self.assertIsInstance(job, cartoframes.context.BatchJobStatus)

        # test batch writes
        n_rows = 550000
        df = pd.DataFrame({'vals': [random.random() for r in range(n_rows)]})

        cc.write(df, self.test_write_batch_table)

        resp = self.sql_client.send('''
            SELECT count(*) AS num_rows FROM {table}
            '''.format(table=self.test_write_batch_table))
        # number of rows same in dataframe and carto table
        self.assertEqual(n_rows, resp['rows'][0]['num_rows'])

        cols = self.sql_client.send('''
            SELECT * FROM {table} LIMIT 1
        '''.format(table=self.test_write_batch_table))
        expected_schema = {'vals': {'type': 'number'},
                           'the_geom': {'type': 'geometry'},
                           'the_geom_webmercator': {'type': 'geometry'},
                           'cartodb_id': {'type': 'number'}}
        # table should be properly created
        # util columns + new column of type number
        self.assertDictEqual(cols['fields'], expected_schema)

        # test properly encoding
        df = pd.DataFrame({'vals': [1, 2], 'strings': ['a', 'ô']})
        cc.write(df, self.test_write_table, overwrite=True)

        # check if table exists
        resp = self.sql_client.send('''
            SELECT *
            FROM {table}
            LIMIT 0
            '''.format(table=self.test_write_table))
        self.assertIsNotNone(resp)

        cc.delete(self.test_write_table)
        df = pd.DataFrame({'vals': list('abcd'), 'ids': list('wxyz')})
        df = df.astype({'vals': str, 'ids': str})
        cc.write(df, self.test_write_table)
        schema = cc.sql_client.send('select ids, vals from {}'.format(
            self.test_write_table))['fields']
        self.assertSetEqual(set([schema[c]['type'] for c in schema]),
                            set(('string', )))

        df = pd.DataFrame({
            'vals': list('abcd'),
            'ids': list('wxyz'),
            'nums': [1.2 * i for i in range(4)],
            'boolvals': [True, False, None, True, ],
            })
        cc.write(df, self.test_write_table, overwrite=True,
                 type_guessing='true')
        resp = cc.sql_client.send('SELECT * FROM {}'.format(
            self.test_write_table))['fields']
        schema = {k: v['type'] for k, v in dict_items(resp)}
        ans = dict(vals='string', ids='string', nums='number',
                   boolvals='boolean', the_geom='geometry',
                   the_geom_webmercator='geometry', cartodb_id='number')
        self.assertDictEqual(schema, ans)

    @unittest.skipIf(WILL_SKIP, 'updates privacy of existing dataset')
    def test_write_privacy(self):
        """context.CartoContext.write Updates the privacy of a dataset"""
        from carto.datasets import DatasetManager
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        ds_manager = DatasetManager(self.auth_client)

        df = pd.DataFrame({'ids': list('abcd'), 'vals': range(4)})
        cc.write(df, self.test_write_table)
        dataset = ds_manager.get(self.test_write_table)
        self.assertEqual(dataset.privacy.lower(), 'private')

        df = pd.DataFrame({'ids': list('efgh'), 'vals': range(4, 8)})
        cc.write(df, self.test_write_table, overwrite=True, privacy='public')
        dataset = ds_manager.get(self.test_write_table)
        self.assertEqual(dataset.privacy.lower(), 'public')

        privacy = cc._get_privacy('i_am_not_a_table_in_this_account')
        self.assertIsNone(privacy)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartocontext_write_index(self):
        """context.CartoContext.write with non-default index"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        df = pd.DataFrame({
                    'vals': range(3),
                    'ids': list('abc')
                },
                index=list('xyz'))
        df.index.name = 'named_index'
        cc.write(df, self.write_named_index)

        df_index = cc.read(self.write_named_index)
        self.assertSetEqual(set(('the_geom', 'vals', 'ids', 'named_index')),
                            set(df_index.columns))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartocontext_mixed_case(self):
        """context.CartoContext.write table name mixed case"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        data = pd.DataFrame({'a': [1, 2, 3],
                             'B': list('abc')})
        cc.write(pd.DataFrame(data), self.mixed_case_table)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartocontext_table_exists(self):
        """context.CartoContext._table_exists"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertFalse(cc._table_exists('acadia_biodiversity'))
        with self.assertRaises(NameError):
            cc._table_exists(self.test_read_table)

    def test_cartocontext_delete(self):
        """context.CartoContext.delete"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        data = {'col1': [1, 2, 3],
                'col2': ['a', 'b', 'c']}
        df = pd.DataFrame(data)

        cc.write(df, self.test_delete_table)
        cc.delete(self.test_delete_table)

        # check that querying recently deleted table raises an exception
        with self.assertRaises(CartoException):
            cc.sql_client.send('select * from {}'.format(
                self.test_delete_table))

        # try to delete a table that does not exists
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            cc.delete('non_existent_table')
            # Verify one warning, subclass is UserWarning, and expected message
            # is in warning
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "Failed to delete" in str(w[-1].message)

    def test_cartocontext_send_dataframe(self):
        """context.CartoContext._send_dataframe"""
        pass

    def test_cartocontext_handle_import(self):
        """context.CartoContext._handle_import"""

        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        import_failures = (
            dict(error_code=8001, state='failure'),
            dict(error_code=6668, state='failure'),
            dict(error_code=1234, state='failure'),
        )

        for import_job in import_failures:
            with self.assertRaises(CartoException):
                cc._handle_import(import_job, 'foo')

        diff_table_err = dict(state='complete',
                              table_name='bar')
        with self.assertRaises(Exception):
            cc._handle_import(diff_table_err, 'foo')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartoframes_sync(self):
        """context.CartoContext.sync"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertIsNone(cc.sync(pd.DataFrame(), 'acadia'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartoframes_query(self):
        """context.CartoContext.query"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        cols = ('link', 'body', 'displayname', 'friendscount', 'postedtime', )
        df = cc.query('''
            SELECT {cols}, '02-06-1429'::date as invalid_df_date
            FROM tweets_obama
            LIMIT 100
            '''.format(cols=','.join(cols)))

        # ensure columns are in expected order
        df = df[list(cols) + ['invalid_df_date']]

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
                           'datetime64[ns]', 'object', )
        self.assertTupleEqual(expected_dtypes,
                              tuple(str(d) for d in df.dtypes),
                              msg='Should have expected schema')

        # empty response
        df_empty = cc.query('''
            SELECT 1
            LIMIT 0
            ''')

        # no rows, one column
        self.assertTupleEqual(df_empty.shape, (0, 1))

        # is a DataFrame
        self.assertIsInstance(df_empty, pd.DataFrame)

        # table already exists, should throw CartoException
        with self.assertRaises(CartoException):
            cc.query('''
                SELECT link, body, displayname, friendscount
                FROM tweets_obama
                LIMIT 100
                ''', table_name='tweets_obama')

        # create a table from a query
        cc.query('''
            SELECT link, body, displayname, friendscount
            FROM tweets_obama
            LIMIT 100
            ''', table_name=self.test_query_table)

        # read newly created table into a dataframe
        df = cc.read(self.test_query_table)
        # should be specified length
        self.assertEqual(len(df), 100)
        # should have requested columns + utility columns from CARTO
        self.assertSetEqual({'link', 'body', 'displayname', 'friendscount',
                             'the_geom', },
                            set(df.columns),
                            msg='Should have the columns requested')

        # see what happens if a query fails after 100 successful rows
        with self.assertRaises(CartoException):
            cc.query('''
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

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_map(self):
        """context.CartoContext.map normal usage"""
        from cartoframes import Layer, QueryLayer, BaseMap
        try:
            import matplotlib
            matplotlib.use('agg')
            import matplotlib.pyplot as plt
        except ImportError:
            plt = None
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        # test with no layers - should produce basemap
        if plt:
            basemap_only_static_mpl = cc.map(interactive=False)
            cartoframes.context.HAS_MATPLOTLIB = False
        basemap_only_static = cc.map(interactive=False)
        basemap_only_interactive = cc.map(interactive=True)

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
        labels_front = cc.map(layers=BaseMap('light', labels='front'))
        self.assertIsInstance(labels_front, IPython.core.display.HTML)

        # test with one Layer
        one_layer = cc.map(layers=Layer('tweets_obama'))
        self.assertIsInstance(one_layer, IPython.core.display.HTML)

        # test with two Layers
        two_layers = cc.map(layers=[Layer('tweets_obama'),
                                    Layer(self.test_read_table)])

        self.assertIsInstance(two_layers, IPython.core.display.HTML)

        # test with one Layer, one QueryLayer
        onelayer_onequery = cc.map(layers=[QueryLayer('''
                                                SELECT *
                                                FROM tweets_obama
                                                LIMIT 100'''),
                                           Layer(self.test_read_table)])

        self.assertIsInstance(onelayer_onequery, IPython.core.display.HTML)

        # test with BaseMap, Layer, QueryLayer
        cc.map(layers=[BaseMap('light'),
                       QueryLayer('''
                               SELECT *
                               FROM tweets_obama
                               LIMIT 100''', color='favoritescount'),
                       Layer(self.test_read_table)])

        # Errors
        # too many layers
        with self.assertRaises(ValueError):
            layers = [Layer('tweets_obama')] * 9
            cc.map(layers=layers)

        # zoom needs to be specified with lng/lat
        with self.assertRaises(ValueError):
            cc.map(lng=44.3386, lat=68.2733)

        # only one basemap layer can be added
        with self.assertRaises(ValueError):
            cc.map(layers=[BaseMap('dark'), BaseMap('light')])

        # only one time layer can be added
        with self.assertRaises(ValueError):
            cc.map(layers=[Layer(self.test_read_table, time='cartodb_id'),
                           Layer(self.test_read_table, time='cartodb_id')])

        # no geometry
        with self.assertRaises(ValueError):
            cc.map(layers=QueryLayer('''
                SELECT
                    null::geometry as the_geom,
                    null::geometry as the_geom_webmercator,
                    row_number() OVER () as cartodb_id
                FROM generate_series(1, 10) as m(i)
                '''))

    @unittest.skipIf(WILL_SKIP, 'no cartocredentials, skipping')
    def test_cartocontext_map_time(self):
        """context.CartoContext.map time options"""
        from cartoframes import Layer
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        html_map = cc.map(layers=Layer(self.test_point_table,
                                       time='cartodb_id'))
        self.assertIsInstance(html_map, IPython.core.display.HTML)

        # category map
        cat_map = cc.map(layers=Layer(self.test_point_table,
                                      time='actor_postedtime',
                                      color='twitter_lang'))
        self.assertRegexpMatches(
                cat_map.__html__(),
                '.*CDB_Math_Mode\(cf_value_twitter_lang\).*')

        with self.assertRaises(
                ValueError,
                msg='cannot create static torque maps currently'):
            cc.map(layers=Layer(self.test_point_table, time='cartodb_id'),
                   interactive=False)

        with self.assertRaises(
                ValueError,
                msg='cannot have more than one torque layer'):
            cc.map(layers=[Layer(self.test_point_table, time='cartodb_id'),
                           Layer(self.test_point_table, color='cartodb_id')])

        with self.assertRaises(
                ValueError,
                msg='cannot do a torque map off a polygon dataset'):
            cc.map(layers=Layer(self.test_read_table, time='cartodb_id'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_map_geom_type(self):
        """context.CartoContext.map basemap geometry type defaults"""
        from cartoframes import Layer, QueryLayer
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        # baseid1 = dark, labels1 = labels on top in named map name
        labels_polygon = cc.map(layers=Layer(self.test_read_table))
        self.assertRegexpMatches(labels_polygon.__html__(),
                                 '.*baseid2_labels1.*',
                                 msg='labels should be on top since only a '
                                     'polygon layer is present')

        # baseid2 = voyager, labels0 = labels on bottom
        labels_point = cc.map(layers=Layer(self.test_point_table))
        self.assertRegexpMatches(labels_point.__html__(),
                                 '.*baseid2_labels0.*',
                                 msg='labels should be on bottom because a '
                                     'point layer is present')

        labels_multi = cc.map(layers=[Layer(self.test_point_table),
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
        multi_geom = cc.map(layers=multi_geom_layer)
        self.assertRegexpMatches(multi_geom.__html__(),
                                 '.*baseid2_labels1.*',
                                 msg='layer has more polys than points, so it '
                                     'should default to polys labels (on top)')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_get_bounds(self):
        """context.CartoContext._get_bounds"""
        from cartoframes.layer import QueryLayer
        cc = cartoframes.CartoContext(base_url=self.baseurl,
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
        extent_ans = cc._get_bounds(layers)

        self.assertDictEqual(extent_ans, ans)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_check_query(self):
        """context.CartoContext._check_query"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        # this table does not exist in this account
        fail_query = '''
            SELECT *
              FROM cyclists
              '''
        fail_cols = ['merckx', 'moser', 'gimondi']
        with self.assertRaises(ValueError):
            cc._check_query(fail_query, style_cols=fail_cols)

        # table exists
        success_query = '''
            SELECT *
              FROM {}
              '''.format(self.test_read_table)
        self.assertIsNone(cc._check_query(success_query))

        # table exists but columns don't
        with self.assertRaises(ValueError):
            cc._check_query(success_query, style_cols=fail_cols)

    def test_df2pg_schema(self):
        """context._df2pg_schema"""
        from cartoframes.context import _df2pg_schema
        data = [{'id': 'a', 'val': 1.1, 'truth': True, 'idnum': 1},
                {'id': 'b', 'val': 2.2, 'truth': True, 'idnum': 2},
                {'id': 'c', 'val': 3.3, 'truth': False, 'idnum': 3}]
        df = pd.DataFrame(data).astype({'id': 'object',
                                        'val': float,
                                        'truth': bool,
                                        'idnum': int})
        # specify order of columns
        df = df[['id', 'val', 'truth', 'idnum']]
        pgcols = ['id', 'val', 'truth', 'idnum']
        ans = ('NULLIF("id", \'\')::text AS id, '
               'NULLIF("val", \'\')::numeric AS val, '
               'NULLIF("truth", \'\')::boolean AS truth, '
               'NULLIF("idnum", \'\')::numeric AS idnum')

        self.assertEqual(ans, _df2pg_schema(df, pgcols))

        # add the_geom
        df['the_geom'] = 'Point(0 0)'
        ans = '\"the_geom\", ' + ans
        pgcols.append('the_geom')
        self.assertEqual(ans, _df2pg_schema(df, pgcols))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_add_encoded_geom(self):
        """context._add_encoded_geom"""
        from cartoframes.context import _add_encoded_geom, _encode_geom
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        # encode_geom=True adds a column called 'geometry'
        df = cc.read(self.test_read_table, limit=5,
                     decode_geom=True)

        # alter the geometry
        df['geometry'] = df['geometry'].apply(lambda x: x.buffer(0.1))

        # the_geom should reflect encoded 'geometry' column
        _add_encoded_geom(df, 'geometry')

        # geometry column should equal the_geom after function call
        self.assertTrue(
                df['the_geom'].equals(df['geometry'].apply(_encode_geom)))

        # don't specify geometry column (should exist since decode_geom==True)
        df = cc.read(self.test_read_table, limit=5,
                     decode_geom=True)
        df['geometry'] = df['geometry'].apply(lambda x: x.buffer(0.2))

        # the_geom should reflect encoded 'geometry' column
        _add_encoded_geom(df, None)

        # geometry column should equal the_geom after function call
        self.assertTrue(
                df['the_geom'].equals(df['geometry'].apply(_encode_geom)))

        df = cc.read(self.test_read_table, limit=5)

        # raise error if 'geometry' column does not exist
        with self.assertRaises(KeyError):
            _add_encoded_geom(df, None)

    def test_decode_geom(self):
        """context._decode_geom"""
        from cartoframes.context import _decode_geom
        # Point (0, 0) without SRID
        ewkb = '010100000000000000000000000000000000000000'
        decoded_geom = _decode_geom(ewkb)
        self.assertEqual(decoded_geom.wkt, 'POINT (0 0)')
        self.assertIsNone(_decode_geom(None))

    def test_encode_geom(self):
        """context._encode_geom"""
        from cartoframes.context import _encode_geom
        from shapely import wkb
        import binascii as ba
        # Point (0 0) without SRID
        ewkb = '010100000000000000000000000000000000000000'
        geom = wkb.loads(ba.unhexlify(ewkb))
        ewkb_resp = _encode_geom(geom)
        self.assertEqual(ewkb_resp, ewkb)
        self.assertIsNone(_encode_geom(None))

    def test_dtypes2pg(self):
        """context._dtypes2pg"""
        from cartoframes.context import _dtypes2pg
        results = {
            'float64': 'numeric',
            'int64': 'numeric',
            'float32': 'numeric',
            'int32': 'numeric',
            'object': 'text',
            'bool': 'boolean',
            'datetime64[ns]': 'timestamp',
            'unknown_dtype': 'text'
        }
        for i in results:
            self.assertEqual(_dtypes2pg(i), results[i])

    def test_pg2dtypes(self):
        """context._pg2dtypes"""
        from cartoframes.context import _pg2dtypes
        results = {
            'date': 'datetime64[ns]',
            'number': 'float64',
            'string': 'object',
            'boolean': 'bool',
            'geometry': 'object',
            'unknown_pgdata': 'object'
        }
        for i in results:
            result = _pg2dtypes(i)
            self.assertEqual(result, results[i])

    def test_debug_print(self):
        """context._debug_print"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey,
                                      verbose=True)
        # request-response usage
        resp = requests.get('http://httpbin.org/get')
        cc._debug_print(resp=resp)
        cc._debug_print(resp=resp.text)

        # non-requests-response usage
        test_str = 'this is a test'
        long_test_str = ', '.join([test_str] * 100)
        self.assertIsNone(cc._debug_print(test_str=test_str))
        self.assertIsNone(cc._debug_print(long_str=long_test_str))

        # verbose = False test
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey,
                                      verbose=False)
        self.assertIsNone(cc._debug_print(resp=test_str))

    def test_data_boundaries(self):
        """context.CartoContext.data_boundaries"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        # all boundary metadata
        boundary_meta = cc.data_boundaries()
        self.assertTrue(boundary_meta.shape[0] > 0,
                        msg='has non-zero number of boundaries')
        meta_cols = set(('geom_id', 'geom_tags', 'geom_type', ))
        self.assertTrue(meta_cols & set(boundary_meta.columns))

        # boundary metadata with correct timespan
        meta_2015 = cc.data_boundaries(timespan='2015')
        self.assertTrue(meta_2015[meta_2015.valid_timespan].shape[0] > 0)

        # test for no data with an incorrect or invalid timespan
        meta_9999 = cc.data_boundaries(timespan='invalid_timespan')
        self.assertTrue(meta_9999[meta_9999.valid_timespan].shape[0] == 0)

        # boundary metadata in a region
        regions = (
            self.test_read_table,
            self.test_data_table,
            [5.9559111595, 45.8179931641, 10.4920501709, 47.808380127],
            'Australia', )
        for region in regions:
            boundary_meta = cc.data_boundaries(region=region)
            self.assertTrue(meta_cols & set(boundary_meta.columns))
            self.assertTrue(boundary_meta.shape[0] > 0,
                            msg='has non-zero number of boundaries')

        #  boundaries for world
        boundaries = cc.data_boundaries(boundary='us.census.tiger.state')
        self.assertTrue(boundaries.shape[0] > 0)
        self.assertEqual(boundaries.shape[1], 2)
        self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                            set(boundaries.columns))

        # boundaries for region
        boundaries = ('us.census.tiger.state', )
        for b in boundaries:
            geoms = cc.data_boundaries(
                boundary=b,
                region=self.test_data_table)
            self.assertTrue(geoms.shape[0] > 0)
            self.assertEqual(geoms.shape[1], 2)
            self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                                set(geoms.columns))

        # presence or lack of clipped boundaries
        nonclipped = (True, False, )
        for tf in nonclipped:
            meta = cc.data_boundaries(include_nonclipped=tf)
            self.assertEqual(
                'us.census.tiger.state' in set(meta.geom_id),
                tf
            )

        with self.assertRaises(ValueError):
            cc.data_boundaries(region=[1, 2, 3])

        with self.assertRaises(ValueError):
            cc.data_boundaries(region=10)

    def test_data_discovery(self):
        """context.CartoContext.data_discovery"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        meta = cc.data_discovery(self.test_read_table,
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
        self.assertTrue(
                (meta['numer_description'].str.contains('poverty')).all()
        )

        # test region = list of lng/lats
        with self.assertRaises(ValueError):
            cc.data_discovery([1, 2, 3])

        switzerland = [5.9559111595, 45.8179931641,
                       10.4920501709, 47.808380127]
        dd = cc.data_discovery(switzerland, keywords='freight', time='2010')
        self.assertEqual(dd['numer_id'][0], 'eu.eurostat.tgs00078')

        dd = cc.data_discovery('Australia',
                               regex='.*Torres Strait Islander.*')
        for nid in dd['numer_id'].values:
            self.assertRegexpMatches(
                    nid,
                    '^au\.data\.B01_Indig_[A-Za-z_]+Torres_St[A-Za-z_]+[FMP]$')

        with self.assertRaises(CartoException):
            cc.data_discovery('non_existent_table_abcdefg')

        dd = cc.data_discovery('United States',
                               boundaries='us.epa.huc.hydro_unit',
                               time=('2006', '2010', ))
        self.assertTrue(dd.shape[0] >= 1)

        poverty = cc.data_discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=False)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertEqual(df_quantiles.shape[0], 0)

        poverty = cc.data_discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=True)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertTrue(df_quantiles.shape[0] > 0)

    def test_data(self):
        """context.CartoContext.data"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        meta = cc.data_discovery(self.test_read_table,
                                 keywords=('poverty', ),
                                 time=('2010 - 2014', ))
        data = cc.data(self.test_data_table, meta)
        anscols = set(meta['suggested_name'])
        origcols = set(cc.read(self.test_data_table, limit=1).columns)
        self.assertSetEqual(anscols, set(data.columns) - origcols)

        meta = [{'numer_id': 'us.census.acs.B19013001',
                 'geom_id': 'us.census.tiger.block_group',
                 'numer_timespan': '2011 - 2015'}, ]
        data = cc.data(self.test_data_table, meta)
        self.assertSetEqual(set(('median_income_2011_2015', )),
                            set(data.columns) - origcols)

        # with self.assertRaises(NotImplementedError):
        #     cc.data(self.test_data_table, meta, how='geom_ref')

        with self.assertRaises(ValueError, msg='no measures'):
            meta = cc.data_discovery('United States', keywords='not a measure')
            cc.data(self.test_read_table, meta)

        with self.assertRaises(ValueError, msg='too many metadata measures'):
            # returns ~180 measures
            meta = cc.data_discovery(region='united states',
                                     keywords='education')
            cc.data(self.test_read_table, meta)

    def test_column_name_collision_do_enrichement(self):
        """context.CartoContext.data column collision"""
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

        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        meta = cc.data_discovery(region=self.test_write_table,
                                 keywords='female')
        meta = meta[meta.suggested_name == dup_col]
        data = cc.data(
            self.test_write_table,
            meta[meta.suggested_name == dup_col]
        )

        self.assertIn('_' + dup_col, data.keys())

    def test_tables(self):
        """context.CartoContext.tables normal usage"""
        cc = cartoframes.CartoContext(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        tables = cc.tables()
        self.assertIsInstance(tables, list)
        self.assertIsInstance(tables[0], cartoframes.analysis.Table)
        self.assertIsNotNone(tables[0].name)
        self.assertIsInstance(tables[0].name, str)

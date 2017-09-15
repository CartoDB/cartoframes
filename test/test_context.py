"""Unit tests for cartoframes.layers"""
import unittest
import os
import sys
import json
import random
import warnings

import cartoframes
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
import pandas as pd

WILL_SKIP = False


class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except:
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

        if self.username and self.apikey:
            self.baseurl = 'https://{username}.carto.com/'.format(
                    username=self.username)
            self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                                api_key=self.apikey)
            self.sql_client = SQLClient(self.auth_client)

        # sets skip value
        WILL_SKIP = self.apikey is None or self.username is None

        # table naming info
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        pyver = sys.version[0:3].replace('.', '_')

        # test tables
        self.test_read_table = 'cb_2013_us_csa_500k'
        self.valid_columns = set(['affgeoid', 'aland', 'awater', 'created_at',
                                  'csafp', 'geoid', 'lsad', 'name', 'the_geom',
                                  'the_geom_webmercator', 'updated_at'])
        # for writing to carto
        self.test_write_table = 'cartoframes_test_table_{ver}_{mpl}'.format(
            ver=pyver,
            mpl=has_mpl)

        # for batch writing to carto
        self.test_write_batch_table = (
            'cartoframes_test_batch_table_{ver}_{mpl}'.format(
                ver=pyver,
                mpl=has_mpl))

        # for queries
        self.test_query_table = ('cartoframes_test_query_'
                                 'table_{ver}_{mpl}'.format(
                                    ver=pyver,
                                    mpl=has_mpl))
        self.test_delete_table = 'cartoframes_test_delete_table_{ver}_{mpl}'.format(
            ver=pyver,
            mpl=has_mpl)

    def tearDown(self):
        """restore to original state"""
        tables = (self.test_write_table,
                  self.test_write_batch_table,
                  self.test_query_table)

        if self.apikey and self.baseurl:
            cc = cartoframes.CartoContext(base_url=self.baseurl,
                                          api_key=self.apikey)
            for table in tables:
                cc.delete(table)
        # TODO: remove the named map templates

    def add_map_template(self):
        """Add generated named map templates to class"""
        pass

    @unittest.skipIf(WILL_SKIP, 'Skipping test, no carto credentials found')
    def test_cartocontext(self):
        """CartoContext.__init__"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertTrue(cc.creds.key() == self.apikey)
        self.assertTrue(cc.creds.base_url() == self.baseurl)
        self.assertTrue(cc.creds.username() == self.username)
        self.assertTrue(not cc.is_org)
        # TODO: how to test instances of a class?
        # self.assertTrue(cc.auth_client.__dict__ == self.auth_client.__dict__)
        # self.assertTrue(cc.sql_client.__dict__ == self.sql_client.__dict__)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_credentials(self):
        """CartoContext.__init__ Credentials argument"""
        creds = cartoframes.Credentials(username=self.username,
                                        key=self.apikey)
        cc = cartoframes.CartoContext(creds=creds)
        self.assertIsInstance(cc, cartoframes.CartoContext)
        self.assertEqual(cc.creds.username(), self.username)
        self.assertEqual(cc.creds.key(), self.apikey)

        # CartoContext pulls from saved credentials
        saved_creds = cartoframes.Credentials(username=self.username,
                                              key=self.apikey)
        saved_creds.save()
        cc_saved = cartoframes.CartoContext()
        self.assertEqual(cc_saved.creds.key(), self.apikey)


    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_isorguser(self):
        """CartoContext._is_org_user"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertTrue(not cc._is_org_user())

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_read(self):
        """CartoContext.read"""
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
        self.assertTrue(set(df.columns) == self.valid_columns)
        self.assertTrue(len(df) == 169)

        # read with limit
        df = cc.read(self.test_read_table, limit=10)
        self.assertEqual(len(df), 10)
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_write(self):
        """CartoContext.write"""
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
        self.assertTrue(resp is not None)

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

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartocontext_table_exists(self):
        """CartoContext._table_exists"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertFalse(cc._table_exists('acadia_biodiversity'))
        with self.assertRaises(NameError):
            cc._table_exists(self.test_read_table)

    def test_cartocontext_delete(self):
        """CartoContext.delete"""
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
        """CartoContext._send_dataframe"""
        pass

    def test_cartocontext_handle_import(self):
        """CartoContext._handle_import"""

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
        """cartoframes.CartoContext.sync"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertIsNone(cc.sync(pd.DataFrame(), 'acadia'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_cartoframes_query(self):
        """cartoframes.CartoContext.query"""
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
        expected_dtypes = ('object', 'object', 'object', 'int64',
                           'datetime64[ns]', 'object', )
        self.assertTupleEqual(expected_dtypes,
                              tuple(str(d) for d in df.dtypes),
                              msg='Should have expected schema')

        # empty response
        df_empty = cc.query('''
            SELECT 1
            LIMIT 0
            ''')

        # no rows or columns
        self.assertTupleEqual(df_empty.shape, (0, 0))

        # is a DataFrame
        self.assertIsInstance(df_empty, pd.DataFrame)

        # table already exists, should throw CartoException
        with self.assertRaises(CartoException):
            _ = cc.query('''
                SELECT link, body, displayname, friendscount
                FROM tweets_obama
                LIMIT 100
                ''', table_name='tweets_obama')

        # create a table from a query
        _ = cc.query('''
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
                             'the_geom', 'the_geom_webmercator'},
                            set(df.columns),
                            msg='Should have the columns requested')

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping this test')
    def test_cartocontext_map(self):
        """CartoContext.map"""
        from cartoframes import Layer, QueryLayer, BaseMap
        try:
            import matplotlib
            matplotlib.use('agg')
            import matplotlib.pyplot as plt
        except ImportError:
            plt = None
        import IPython
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
        _ = cc.map(layers=[BaseMap('light'),
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

        # time layers are not implemented yet
        with self.assertRaises(NotImplementedError):
            cc.map(layers=Layer(self.test_read_table, time='cartodb_id'))

    @unittest.skipIf(WILL_SKIP, 'no carto credentials, skipping')
    def test_get_bounds(self):
        """CartoContext._get_bounds"""
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
        """CartoContext._check_query"""
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
            'datetime64[ns]': 'date',
            'unknown_dtype': 'text'
        }
        for i in results:
            result = _dtypes2pg(i)
            self.assertEqual (result, results[i])

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
            self.assertEqual (result, results[i])

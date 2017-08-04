"""Unit tests for cartoframes.layers"""
import unittest
import os
import sys
import json
import random
import cartoframes
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
import pandas as pd

class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    def setUp(self):
        if (os.environ.get('APIKEY') is None or
            os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
            except FileNotFoundError:
                print("Create a `secret.json` file by renaming "
                      "`secret.json.sample` to `secret.json` and updating "
                      "the credentials to match your environment.")
                raise
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
        self.baseurl = 'https://{username}.carto.com/'.format(username=self.username)
        self.valid_columns = set(['the_geom', 'the_geom_webmercator', 'lsad10',
                                  'name10', 'geoid10', 'affgeoid10', 'pumace10',
                                  'statefp10', 'awater10', 'aland10','updated_at',
                                  'created_at'])
        self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                            api_key=self.apikey)
        self.sql_client = SQLClient(self.auth_client)
        self.test_read_table = 'cb_2013_puma10_500k'
        self.test_write_table = 'cartoframes_test_table_{ver}'.format(
            ver=sys.version[0:3].replace('.', '_'))
        self.test_query_table = 'cartoframes_test_query_table_{ver}'.format(
            ver=sys.version[0:3].replace('.', '_'))


    def tearDown(self):
        """restore to original state"""
        self.sql_client.send('''
            DROP TABLE IF EXISTS "{}"
            '''.format(self.test_write_table))
        self.sql_client.send('''
            DROP TABLE IF EXISTS "{}"
            '''.format(self.test_query_table))

        # TODO: remove the named map templates

    def add_map_template(self):
        """Add generated named map templates to class"""
        pass

    def test_cartocontext(self):
        """CartoContext.__init__"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertTrue(cc.api_key == self.apikey)
        self.assertTrue(cc.base_url == self.baseurl)
        self.assertTrue(cc.username == self.username)
        self.assertTrue(not cc.is_org)
        # TODO: how to test instances of a class?
        # self.assertTrue(cc.auth_client.__dict__ == self.auth_client.__dict__)
        # self.assertTrue(cc.sql_client.__dict__ == self.sql_client.__dict__)

    def test_cartocontext_isorguser(self):
        """CartoContext._is_org_user"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                              api_key=self.apikey)
        self.assertTrue(not cc._is_org_user())

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
        self.assertTrue(len(df) == 2379)

        # read with limit
        df = cc.read(self.test_read_table, limit=10)
        self.assertEqual(len(df), 10)
        self.assertIsInstance(df, pd.DataFrame)

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

    def test_cartocontext_table_exists(self):
        """CartoContext._table_exists"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertFalse(cc._table_exists('acadia_biodiversity'))
        with self.assertRaises(NameError):
            cc._table_exists(self.test_read_table)


    def test_cartocontext_send_dataframe(self):
        """CartoContext._send_dataframe"""
        pass

    def test_cartoframes_sync(self):
        """cartoframes.CartoContext.sync"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        self.assertIsNone(cc.sync(pd.DataFrame(), 'acadia'))

    def test_cartoframes_query(self):
        """cartoframes.CartoContext.query"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        df = cc.query('''
            SELECT link, body, displayname, friendscount
            FROM tweets_obama
            LIMIT 100
            ''')
        # same number of rows
        self.assertEqual(len(df), 100,
                         msg='Expected number or rows')
        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        self.assertSetEqual({'link', 'body', 'displayname', 'friendscount'},
                            set(df.columns),
                            msg='Should have the columns requested')

        # table already exists, should throw CartoException
        with self.assertRaises(CartoException):
            df_create_table = cc.query('''
                SELECT link, body, displayname, friendscount
                FROM tweets_obama
                LIMIT 100
                ''',
                table_name='tweets_obama')

        # create a table from a query
        _ = cc.query('''
            SELECT link, body, displayname, friendscount
            FROM tweets_obama
            LIMIT 100
            ''',
            table_name=self.test_query_table)

        # read newly created table into a dataframe
        df = cc.read(self.test_query_table)
        # should be specified length
        self.assertEqual(len(df), 100)
        # should have requested columns + utility columns from CARTO
        self.assertSetEqual({'link', 'body', 'displayname', 'friendscount',
                             'the_geom', 'the_geom_webmercator'},
                            set(df.columns),
                            msg='Should have the columns requested')

    def test_cartocontext_map(self):
        """CartoContext.map"""
        from cartoframes import Layer, QueryLayer, BaseMap
        import IPython
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        # test with no layers - should produce basemap
        basemap_only_static = cc.map(interactive=False)
        basemap_only_interactive = cc.map(interactive=True)

        # are of instance of IPython HTML class
        self.assertIsInstance(basemap_only_static,
                              IPython.core.display.HTML)
        self.assertIsInstance(basemap_only_interactive,
                              IPython.core.display.HTML)

        # have the HTML innards that are to be expected
        if sys.version[0] == 3:
            self.assertRegex(basemap_only_static.data,
                    '^<img src="https://.*api/v1/map/static/named/cartoframes_ver.*" />$')
            self.assertRegex(basemap_only_interactive.data,
                             '^<iframe srcdoc="<!DOCTYPE html>.*')
        elif sys.version[0] == 2:
            self.assertRegexMatches(
                basemap_only_static.data,
                '^<img src="https://.*api/v1/map/static/named/cartoframes_ver.*" />$')
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
        oneeach = cc.map(layers=[BaseMap('light'),
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


    def test_get_bounds(self):
        """CartoContext._get_bounds"""
        from cartoframes.layer import Layer, QueryLayer
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

    def test_df2pg_schema(self):
        """cartoframes._df2pg_schema"""
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
        ans = ('NULLIF("id", \'\')::text AS id, '
               'NULLIF("val", \'\')::numeric AS val, '
               'NULLIF("truth", \'\')::boolean AS truth, '
               'NULLIF("idnum", \'\')::numeric AS idnum')

        self.assertEqual(ans, _df2pg_schema(df))

        # add the_geom
        df['the_geom'] = 'Point(0 0)'
        ans = '\"the_geom\", ' + ans
        self.assertEqual(ans, _df2pg_schema(df))

    def test_drop_tables_query(self):
        """cartoframes._drop_tables_query"""
        from cartoframes.context import _drop_tables_query
        tables = ['table1', 'table2', 'table3']
        ans = ('DROP TABLE IF EXISTS table1;\n'
               'DROP TABLE IF EXISTS table2;\n'
               'DROP TABLE IF EXISTS table3;')
        self.assertEqual(ans, _drop_tables_query(tables))

    def test_add_encoded_geom(self):
        """context._add_encoded_geom"""
        from cartoframes.context import _add_encoded_geom, _encode_geom
        # import shapely
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
        print(df['the_geom'])
        print(df['geometry'].apply(_encode_geom))
        self.assertTrue(df['the_geom'].equals(df['geometry'].apply(_encode_geom)))

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

# -*- coding: utf-8 -*-
"""Unit tests for cartoframes.contrib.vector"""
import unittest
import os
import sys
import json
import random
import warnings
import requests

import cartoframes
from cartoframes.contrib import vector
from carto.exceptions import CartoException
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from pyrestcli.exceptions import NotFoundException
import pandas as pd

from utils import _UserUrlLoader
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
from IPython.display import HTML

WILL_SKIP = False
warnings.filterwarnings("ignore")


class TestContribVector(unittest.TestCase, _UserUrlLoader):
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

        # sets skip value
        WILL_SKIP = self.apikey is None or self.username is None  # noqa: F841
        
        self.points = 'tweets_obama'
        self.polys = 'nat'
        self.local = 'cb_2013_us_csa_500k'


    def test_vector_multilayer(self):
        """contrib.vector"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        layers = [
            vector.Layer(self.points, color='red', size=10, strokeColor='blue'),
            vector.QueryLayer(
                'SELECT * FROM {}'.format(self.polys),
                time='torque($cartodb_id, 10)', strokeWidth=2)
        ]
        self.assertIsInstance(vector.vmap(layers, cc), HTML)

    @unittest.skipIf(not HAS_GEOPANDAS, 'GeoPandas not installed')
    def test_vector_local(self):
        """contrib.vector"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        df = gpd.GeoDataFrame(
            cc.query('''
                select the_geom, the_geom_webmercator, cartodb_id
                from {}
            '''.format(self.local),
            decode_geom=True)
        )
        layers = [
            vector.Layer(self.points, color='red', size=10, strokeColor='blue'),
            vector.QueryLayer(
                'SELECT * FROM {}'.format(self.polys),
                time='torque($cartodb_id, 10)', strokeWidth=2),
            vector.LocalLayer(df)
        ]
        self.assertIsInstance(vector.vmap(layers, cc), HTML)

    @unittest.skipIf(HAS_GEOPANDAS, 'GeoPandas installed, so not needed')
    def test_vector_local(self):
        """contrib.vector local with"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        with self.assertRaises(ValueError):
            df = cc.query('''
                    select the_geom, the_geom_webmercator, cartodb_id
                    from {}
                '''.format(self.local),
                decode_geom=True)
            layers = [
                vector.Layer(self.points, color='red', size=10, strokeColor='blue'),
                vector.QueryLayer(
                    'SELECT * FROM {}'.format(self.polys),
                    time='torque($cartodb_id, 10)', strokeWidth=2),
                vector.LocalLayer(df)
            ]
            self.assertIsInstance(vector.vmap(layers, cc), HTML)

    def test_vector_interactivity(self):
        """contrib.vector"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        layers = [
            vector.Layer(self.points, interactivity='body'),
            vector.QueryLayer(
                'SELECT * FROM {}'.format(self.polys),
                interactivity=['name', 'state_name', ]),
            vector.QueryLayer(
                'SELECT * FROM {}'.format(self.polys),
                interactivity={
                    'cols': ['name', 'state_name', ],
                    'header': '<h1 class="h1">NAT</h1>',
                    'event': 'click'
                })
        ]
        self.assertIsInstance(vector.vmap(layers, cc), HTML)

        # invalid entry for interactivity
        with self.assertRaises(ValueError):
            vector.vmap([vector.Layer(self.points, interactivity=10), ])

    def test_vector_basemaps(self):
        """contrib.vector.BaseMaps"""
        self.assertEquals(vector.BaseMaps.positron, 'Positron')
        self.assertEquals(vector.BaseMaps.darkmatter, 'DarkMatter')
        self.assertEquals(vector.BaseMaps.voyager, 'Voyager')
        with self.assertRaises(AttributeError):
            b = vector.BaseMaps.doesntexist

    def test_vector_vmap_basemap(self):
        """contrib.vector.vmap with basemap flag"""
        cc = cartoframes.CartoContext(
            base_url=self.baseurl,
            api_key=self.apikey
        )
        with self.assertRaises(ValueError, msg='style key not in basemap'):
            vector.vmap(
                [vector.Layer(self.points), ],
                context=cc,
                basemap={'tiles': 'abc123'}
            )


        vector.vmap(
            [vector.Layer(self.points), ],
            context=cc,
            basemap={'style': 'mapbox://styles/mapbox/streets-v9'}
        )

    def test_vector__combine_bounds(self):
        """test vector._combine_bounds"""
        WORLD = {'west': -180, 'south': -85.1, 'east': 180, 'north': 85.1}
        NONE_BBOX = dict.fromkeys(('west', 'south', 'east', 'north'))
        with self.assertRaises(AssertionError, msg='must have all keys'):
            vector._combine_bounds(
                    {'west': -10, 'south': -10, 'north': 10},
                    {'west': 0, 'south': -20, 'east': 10, 'north': 20}
            )

        # empty dicts give the world
        self.assertDictEqual(
            vector._combine_bounds({}, {}),
            WORLD,
            msg='empty dicts give the world'
        )

        # none filled bboxes
        self.assertDictEqual(
            vector._combine_bounds(NONE_BBOX, NONE_BBOX),
            WORLD,
            msg='if bboxes are None, use the world'
        )

        # none filled and empty bboxes
        self.assertDictEqual(
            vector._combine_bounds({}, NONE_BBOX),
            WORLD,
            msg='if bboxes are None and empty, use the world'
        )
        # normal usage
        # normal with none filled
        bbox1 = {'west': -10, 'south': -10, 'east': 0, 'north': 0}
        self.assertDictEqual(
            vector._combine_bounds(bbox1, NONE_BBOX),
            bbox1,
            msg='valid bbox and none bbox give valid bbox'
        )

        # two normal bboxes
        bbox1 = {'west': -10, 'south': -10, 'east': 0, 'north': 0}
        bbox2 = {'west': 0, 'south': 0, 'east': 10, 'north': 10}
        self.assertDictEqual(
            vector._combine_bounds(bbox1, bbox2),
            {'west': -10, 'south': -10, 'east': 10, 'north': 10},
            msg='valid bbox and none bbox give valid bbox'
        )

    @unittest.skipIf(not HAS_GEOPANDAS, 'no tests if geopandas is not present')
    def test_vector__get_bounds_local(self):
        """"""
        def makegdf(lats, lngs):
            """make a geodataframe from coords"""
            from shapely.geometry import Point
            df = pd.DataFrame({
                'Latitude': lats,
                'Longitude': lngs
            })
            df['Coordinates'] = list(zip(df.Longitude, df.Latitude))
            df['Coordinates'] = df['Coordinates'].apply(Point)
            return gpd.GeoDataFrame(df, geometry='Coordinates')

        # normal usage
        llayer1 = vector.LocalLayer(makegdf([-10, 0], [-10, 0]))
        llayer2 = vector.LocalLayer(makegdf([0, 10], [0, 10]))
        self.assertDictEqual(
            vector._get_bounds_local([llayer1, llayer2]),
            {'west': -10, 'south': -10, 'east': 10, 'north': 10},
            msg='local bounding boxes combine'
        )

        # single layer
        llayer1 = vector.LocalLayer(makegdf([-10, 10], [-10, 10]))
        self.assertDictEqual(
            vector._get_bounds_local([llayer1, ]),
            {'west': -10, 'south': -10, 'east': 10, 'north': 10},
            msg='local bounding boxes combine'
        )

        # no layers
        self.assertDictEqual(
            vector._get_bounds_local([]),
            {'west': None, 'south': None, 'east': None, 'north': None}
        )

    def test_vector__get_super_bounds(self):
        """"""
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        qlayer = cartoframes.QueryLayer('''
            SELECT
                the_geom,
                ST_Transform(the_geom, 3857) as the_geom_webmercator,
                1 as cartodb_id
            FROM (
                SELECT ST_MakeEnvelope(-10, -10, 0, 0, 4326) as the_geom
            ) _w
        ''')

        ans = '[[-10.0, -10.0], [0.0, 0.0]]'
        self.assertEqual(
            ans,
            vector._get_super_bounds([qlayer, ], cc),
            msg='super bounds are equal'
        )

        if HAS_GEOPANDAS:
            ldata = gpd.GeoDataFrame(
                cc.query(
                    '''
                    SELECT
                        the_geom,
                        ST_Transform(the_geom, 3857) as the_geom_webmercator,
                        1 as cartodb_id
                    FROM (
                        SELECT ST_MakeEnvelope(0, 0, 10, 10, 4326) as the_geom
                    ) _w
                    ''',
                    decode_geom=True
                )
            )
            llayer = vector.LocalLayer(ldata)
            ans = '[[-10.0, -10.0], [10.0, 10.0]]'
            self.assertEqual(
                ans,
                vector._get_super_bounds([qlayer, llayer], cc),
                msg='super bounds are equal'
            )

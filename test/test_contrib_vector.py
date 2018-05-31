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
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
from IPython.display import HTML

WILL_SKIP = False
warnings.filterwarnings("ignore")


class _UserUrlLoader:
    def user_url(self):
        user_url = None
        if (os.environ.get('USERURL') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                user_url = creds['USERURL']
            except:
                warnings.warn('secret.json not found')

        if user_url in (None, ''):
            user_url = 'https://{username}.carto.com/'

        return user_url


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

        # sets client to be ci
        if not cartoframes.context.DEFAULT_SQL_ARGS['client']\
                .endswith('_dev_ci'):
            cartoframes.context.DEFAULT_SQL_ARGS['client'] += '_dev_ci'
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

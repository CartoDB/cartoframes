# -*- coding: utf-8 -*-

import unittest

from cartoframes import context
from cartoframes.viz import Map, Layer, Source
from cartoframes.data import StrategiesRegistry
from cartoframes.auth import Credentials

from ..mocks.kuviz_mock import KuvizPublisherMock, _create_kuviz, PRIVACY_PUBLIC, PRIVACY_PASSWORD
from ..mocks.dataset_mock import DatasetMock
from ..mocks.context_mock import ContextMock

from .utils import build_geojson


class TestKuviz(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

        self.html = "<html><body><h1>Hi Kuviz yeee</h1></body></html>"

    def tearDown(self):
        StrategiesRegistry.instance = None

    def test_kuviz_create(self):
        name = 'test-name'
        kuviz = _create_kuviz(credentials=self.credentials, html=self.html, name=name)
        self.assertIsNotNone(kuviz.id)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, PRIVACY_PUBLIC)

    def test_kuviz_create_with_password(self):
        name = 'test-name'
        kuviz = _create_kuviz(credentials=self.credentials, html=self.html, name=name, password="1234")
        self.assertIsNotNone(kuviz.id)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, PRIVACY_PASSWORD)


class TestKuvizPublisher(unittest.TestCase):
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
        StrategiesRegistry.instance = None

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        self.assertIsNotNone(kuviz_dict['id'])
        self.assertIsNotNone(kuviz_dict['url'])
        self.assertEqual(kuviz_dict['name'], name)
        self.assertEqual(kuviz_dict['privacy'], privacy)

    def test_kuviz_publisher_create_local(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        source_2 = Source(build_geojson([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        vmap = Map([
            layer_1,
            layer_2
        ])

        kp = KuvizPublisherMock(vmap.layers)
        self.assertNotEqual(kp._layers, vmap.layers)
        self.assertEqual(len(kp._layers), len(vmap.layers))

    def test_kuviz_publisher_has_layers_copy(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kp = KuvizPublisherMock(vmap.layers)
        self.assertEqual(len(kp._layers), len(vmap.layers))

        kp._layers = []
        self.assertNotEqual(len(kp._layers), len(vmap.layers))

    def test_kuviz_publisher_from_local_sync(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kp = KuvizPublisherMock(vmap.layers)
        self.assertEqual(kp.is_sync(), False)

    def test_kuviz_publisher_create_remote(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        self.assertNotEqual(kp._layers, vmap.layers)
        self.assertEqual(len(kp._layers), len(vmap.layers))

    def test_kuviz_publisher_create_remote_sync(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        self.assertEqual(kp.is_sync(), True)

    def test_kuviz_publisher_unsync(self):
        dataset = DatasetMock(build_geojson([-10, 0], [-10, 0]))
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        self.assertEqual(kp.is_sync(), False)

    def test_kuviz_publisher_sync_layers(self):
        dataset = DatasetMock(build_geojson([-10, 0], [-10, 0]))
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        kp.sync_layers(table_name='fake_table', credentials=self.credentials)
        self.assertEqual(kp.is_sync(), True)

    def test_kuviz_publisher_get_layers_defaul_apikey(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        kp.set_credentials(self.credentials)
        layers = kp.get_layers()

        self.assertEqual(layers[0].source.dataset.credentials, self.credentials)
        self.assertEqual(
            layers[0].credentials,
            {'username': self.username,
             'api_key': 'default_public',
             'base_url': 'https://{}.carto.com'.format(self.username)})

    def test_kuviz_publisher_get_layers_with_api_key(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(vmap.layers)
        kp.set_credentials(self.credentials)
        maps_api_key = '1234'
        layers = kp.get_layers(maps_api_key=maps_api_key)

        self.assertEqual(layers[0].source.dataset.credentials, self.credentials)
        self.assertEqual(
            layers[0].credentials,
            {'username': self.username,
             'api_key': maps_api_key,
             'base_url': 'https://{}.carto.com'.format(self.username)})

    def test_kuviz_publisher_all(self):
        kuviz_dicts = KuvizPublisherMock.all()
        for kuviz_dict in kuviz_dicts:
            self.assert_kuviz_dict(kuviz_dict, name="test", privacy=PRIVACY_PUBLIC)

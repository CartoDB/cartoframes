# -*- coding: utf-8 -*-

import unittest

from carto.exceptions import CartoException

from cartoframes.viz.kuviz import _validate_carto_kuviz
from cartoframes.viz import Map, Layer, Source

from mocks.kuviz_mock import KuvizMock, CartoKuvizMock, KuvizPublisherMock
from mocks.context_mock import ContextMock
from mocks.dataset_mock import DatasetMock

from .utils import build_geojson


class TestKuviz(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.context = ContextMock(username=self.username, api_key=self.api_key)

        self.html = "<html><body><h1>Hi Kuviz yeee</h1></body></html>"

    def test_kuviz_create(self):
        name = 'test-name'
        kuviz = KuvizMock.create(context=self.context, html=self.html, name=name)
        self.assertIsNotNone(kuviz.vid)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, KuvizMock.PRIVACY_PUBLIC)

    def test_kuviz_create_with_password(self):
        name = 'test-name'
        kuviz = KuvizMock.create(context=self.context, html=self.html, name=name, password="1234")
        self.assertIsNotNone(kuviz.vid)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, KuvizMock.PRIVACY_PASSWORD)

    def test_kuviz_create_fails_without_all_fields(self):
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            KuvizMock.create(context=self.context, html=self.html, name=None)

    def test_kuviz_validation(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, password=None)
        result = _validate_carto_kuviz(carto_kuviz)
        self.assertTrue(result)

    def test_kuviz_validation_with_password(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, password="1234")
        result = _validate_carto_kuviz(carto_kuviz)
        self.assertTrue(result)

    def test_kuviz_validation_fails_without_id(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, id=None, password=None)
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            _validate_carto_kuviz(carto_kuviz)

    def test_kuviz_validation_fails_without_url(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, url=None, password=None)
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            _validate_carto_kuviz(carto_kuviz)


class TestKuvizPublisher(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.context = ContextMock(username=self.username, api_key=self.api_key)

    def test_kuviz_publisher_create_local(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        source_2 = Source(build_geojson([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        map = Map([
            layer_1,
            layer_2
        ])

        kp = KuvizPublisherMock(map)
        self.assertEqual(kp._context, None)
        self.assertNotEqual(kp._layers, map.layers)
        self.assertEqual(len(kp._layers), len(map.layers))

    def test_kuviz_publisher_has_layers_copy(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        map = Map(layer_1)

        kp = KuvizPublisherMock(map)
        self.assertEqual(len(kp._layers), len(map.layers))

        kp._layers = []
        self.assertNotEqual(len(kp._layers), len(map.layers))

    def test_kuviz_publisher_from_local_sync(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        map = Map(layer_1)

        kp = KuvizPublisherMock(map)
        self.assertEqual(kp.is_sync(), False)

    def test_kuviz_publisher_create_remote(self):
        dataset = DatasetMock.from_table(table_name='fake_table', context=self.context)
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        self.assertEqual(kp._context, None)
        self.assertNotEqual(kp._layers, map.layers)
        self.assertEqual(len(kp._layers), len(map.layers))

    def test_kuviz_publisher_create_remote_sync(self):
        dataset = DatasetMock.from_table(table_name='fake_table', context=self.context)
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        self.assertEqual(kp.is_sync(), True)

    def test_kuviz_publisher_unsync(self):
        dataset = DatasetMock.from_table(table_name='fake_table', context=self.context)
        dataset._is_saved_in_carto = False
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        self.assertEqual(kp.is_sync(), False)

    def test_kuviz_publisher_sync_layers(self):
        query = "SELECT 1"
        dataset = DatasetMock.from_query(query=query, context=self.context)
        dataset._is_saved_in_carto = False
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        kp._layers[0].source.dataset = dataset
        kp.sync_layers(table_name='fake_table', context=self.context)
        self.assertEqual(kp.is_sync(), True)

    def test_kuviz_publisher_get_layers_defaul_apikey(self):
        dataset = DatasetMock.from_table(table_name='fake_table', context=self.context)
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        kp.set_context(self.context)
        layers = kp.get_layers()

        self.assertEqual(layers[0].source.dataset._cc, self.context)
        self.assertEqual(
            layers[0].source.credentials,
            {'username': self.username, 'api_key': 'default_public', 'base_url': self.username})

    def test_kuviz_publisher_get_layers_with_api_key(self):
        dataset = DatasetMock.from_table(table_name='fake_table', context=self.context)
        map = Map(Layer(Source(dataset)))

        kp = KuvizPublisherMock(map)
        kp.set_context(self.context)
        maps_api_key = '1234'
        layers = kp.get_layers(maps_api_key=maps_api_key)

        self.assertEqual(layers[0].source.dataset._cc, self.context)
        self.assertEqual(
            layers[0].source.credentials,
            {'username': self.username, 'api_key': maps_api_key, 'base_url': self.username})

# -*- coding: utf-8 -*-

import unittest

from cartoframes.lib import context
from cartoframes.viz import Map, Layer, Source
from cartoframes.data import Dataset, StrategiesRegistry
from cartoframes.auth import Credentials
from cartoframes.data.clients.auth_api_client import AuthAPIClient
from cartoframes.viz.kuviz import KuvizPublisher, DEFAULT_PUBLIC

from ..mocks.context_mock import ContextMock

from .utils import build_geojson

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

TOKEN_MOCK = '1234'


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

    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_instantiation(self, _create_auth_client_mock, _get_kuviz_manager_mock):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None

        kuviz_publisher = KuvizPublisher(None)

        assert isinstance(kuviz_publisher, KuvizPublisher)
        assert kuviz_publisher._maps_api_key == DEFAULT_PUBLIC
        assert kuviz_publisher._layers == []

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_set_layers(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(Dataset('fake_table', self.credentials))

        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        source_2 = Source(build_geojson([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        vmap = Map([
            layer_1,
            layer_2
        ])

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        self.assertNotEqual(kuviz_publisher._layers, vmap.layers)
        self.assertEqual(len(kuviz_publisher._layers), len(vmap.layers))

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_has_layers_copy(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(Dataset('fake_table', self.credentials))

        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')
        self.assertEqual(len(kuviz_publisher._layers), len(vmap.layers))

        vmap.layers = []
        self.assertNotEqual(len(kuviz_publisher._layers), len(vmap.layers))
        self.assertGreater(len(kuviz_publisher._layers), 0)

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_from_local_is_sync(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(Dataset('fake_table', self.credentials))

        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        layers = kuviz_publisher.get_layers()

        self.assertEqual(vmap.layers[0].source.dataset.is_local(), True)
        self.assertEqual(layers[0].source.dataset.is_remote(), True)

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_with_public_use_defaul_public(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(Dataset('fake_table', self.credentials))

        dataset = Dataset('fake_table', credentials=self.credentials)
        vmap = Map(Layer(dataset))

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        layers = kuviz_publisher.get_layers()

        self.assertEqual(layers[0].source.dataset.credentials, self.credentials)
        self.assertEqual(
            layers[0].credentials,
            {'username': self.username,
             'api_key': DEFAULT_PUBLIC,
             'base_url': 'https://{}.carto.com'.format(self.username)})

    @patch.object(Dataset, 'is_public')
    @patch.object(AuthAPIClient, 'create_api_key')
    @patch('cartoframes.data.clients.auth_api_client._get_api_key_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_private_dataset_create_new_apikey(self, _create_auth_client_mock, _get_api_key_manager,
                                                     create_api_key, is_public):
        token = '1234'

        _create_auth_client_mock.return_value = None
        create_api_key.return_value = token
        _get_api_key_manager.return_value = None
        is_public.return_value = False

        dataset = Dataset('fake_table', credentials=self.credentials)
        layers = [Layer(dataset)]

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher._layers = layers

        kuviz_publisher._manage_maps_api_key('fake_name')
        assert kuviz_publisher._maps_api_key == token

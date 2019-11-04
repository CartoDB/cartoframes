# -*- coding: utf-8 -*-

import pytest

from carto.exceptions import CartoException

from cartoframes.lib import context
from cartoframes.viz import Map, Layer, Source
from cartoframes.data import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.data.clients.auth_api_client import AuthAPIClient
from cartoframes.viz.kuviz import KuvizPublisher, DEFAULT_PUBLIC, kuviz_to_dict

from ..mocks.context_mock import ContextMock
from ..mocks.kuviz_mock import CartoKuvizMock

from .utils import build_geojson

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

TOKEN_MOCK = '1234'


class TestKuvizPublisher():
    def setup_method(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)
        self._context_mock = ContextMock()

        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock

    def teardown_method(self):
        context.create_context = self.original_create_context

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        assert kuviz_dict['id'] is not None
        assert kuviz_dict['url'] is not None
        assert kuviz_dict['name'] == name
        assert kuviz_dict['privacy'] == privacy

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
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))

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

        assert kuviz_publisher._layers != vmap.layers
        assert len(kuviz_publisher._layers) == len(vmap.layers)

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_has_layers_copy(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))

        source_1 = Source(CartoDataFrame('fake_table_2', credentials=self.credentials, download=False))
        layer_1 = Layer(source_1)
        vmap = Map([layer_1])

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        assert len(kuviz_publisher._layers) == len(vmap.layers)
        assert kuviz_publisher._layers == vmap.layers

        vmap.layers = []
        assert len(kuviz_publisher._layers) != len(vmap.layers)
        assert len(kuviz_publisher._layers) > 0

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_from_local_is_sync(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))

        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        layers = kuviz_publisher.get_layers()

        assert vmap.layers[0].source.cdf.is_local() is True
        assert layers[0].source.cdf.is_remote() is True

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_use_defaul_public(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        vmap = Map(Layer(cdf))

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        layers = kuviz_publisher.get_layers()

        assert layers[0].source.cdf._strategy.credentials == self.credentials
        assert layers[0].credentials == ({
            'username': self.username,
            'api_key': DEFAULT_PUBLIC,
            'base_url': 'https://{}.carto.com'.format(self.username)})

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_use_only_base_url(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _base_url_credentials = Credentials(base_url='https://fakeuser.carto.com')
        _sync_layer.return_value = Layer(CartoDataFrame(
            'fake_table', credentials=_base_url_credentials, download=False))

        cdf = CartoDataFrame('fake_table', credentials=_base_url_credentials, download=False)
        vmap = Map(Layer(cdf))

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_name', 'fake_table_name')

        layers = kuviz_publisher.get_layers()

        assert layers[0].source.cdf._strategy.credentials == _base_url_credentials
        assert layers[0].credentials == ({
            'username': 'user',  # Default VL username
            'api_key': DEFAULT_PUBLIC,
            'base_url': 'https://fakeuser.carto.com'})

    @patch.object(CartoDataFrame, 'is_public')
    @patch.object(AuthAPIClient, 'create_api_key')
    @patch('cartoframes.data.clients.auth_api_client._get_api_key_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_create_new_apikey(self, _create_auth_client_mock, _get_api_key_manager,
                                               create_api_key, is_public):
        token = '1234'

        _create_auth_client_mock.return_value = None
        create_api_key.return_value = token
        _get_api_key_manager.return_value = None
        is_public.return_value = False

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        layers = [Layer(cdf)]

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher._layers = layers

        assert kuviz_publisher._maps_api_key == DEFAULT_PUBLIC
        kuviz_publisher._manage_maps_api_key('fake_name')
        assert kuviz_publisher._maps_api_key == token

    @patch('cartoframes.viz.kuviz._create_kuviz')
    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_publish(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer,
                                     _create_kuviz):
        kuviz = CartoKuvizMock('fake_kuviz')

        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))
        _create_kuviz.return_value = kuviz

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        vmap = Map(Layer(cdf))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, kuviz_name, 'fake_table_name')
        result = kuviz_publisher.publish(html, kuviz_name)

        assert kuviz_publisher.kuviz == kuviz
        assert result == kuviz_to_dict(kuviz)

    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_update_fail(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer):
        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        vmap = Map(Layer(cdf))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, kuviz_name, 'fake_table_name')

        with pytest.raises(CartoException):
            kuviz_publisher.update(html, kuviz_name, None)

    @patch('cartoframes.viz.kuviz._create_kuviz')
    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_update(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer,
                                    _create_kuviz):
        kuviz = CartoKuvizMock('fake_kuviz')

        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))
        _create_kuviz.return_value = kuviz

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        vmap = Map(Layer(cdf))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, kuviz_name, 'fake_table_name')
        result_publish = kuviz_publisher.publish(html, kuviz_name)

        kuviz.name = 'fake_name_2'
        result_update = kuviz_publisher.update(html, kuviz_name, None)

        assert kuviz_publisher.kuviz == kuviz
        assert result_update == kuviz_to_dict(kuviz)
        assert result_publish != kuviz_to_dict(kuviz)

    @patch('cartoframes.viz.kuviz._create_kuviz')
    @patch.object(KuvizPublisher, '_sync_layer')
    @patch('cartoframes.viz.kuviz._get_kuviz_manager')
    @patch('cartoframes.viz.kuviz._create_auth_client')
    def test_kuviz_publisher_delete(self, _create_auth_client_mock, _get_kuviz_manager_mock, _sync_layer,
                                    _create_kuviz):
        kuviz = CartoKuvizMock('fake_kuviz')

        _create_auth_client_mock.return_value = None
        _get_kuviz_manager_mock.return_value = None
        _sync_layer.return_value = Layer(CartoDataFrame('fake_table', credentials=self.credentials, download=False))
        _create_kuviz.return_value = kuviz

        cdf = CartoDataFrame('fake_table', credentials=self.credentials, download=False)
        vmap = Map(Layer(cdf))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, kuviz_name, 'fake_table_name')
        kuviz_publisher.publish(html, kuviz_name)

        kuviz_publisher.delete()

        assert kuviz_publisher.kuviz is None

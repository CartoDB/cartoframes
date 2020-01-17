# -*- coding: utf-8 -*-

import pytest

from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer
from cartoframes.viz.source import Source
from cartoframes.viz.kuviz import KuvizPublisher, DEFAULT_PUBLIC, kuviz_to_dict
from cartoframes.io.managers.context_manager import ContextManager

from ..mocks.kuviz_mock import CartoKuvizMock
from ..mocks.api_key_mock import APIKeyManagerMock

from .utils import build_geodataframe


def setup_mocks(mocker, credentials, is_public=True, token=None):
    mocker.patch(
        'cartoframes.data.clients.auth_api_client._get_api_key_manager',
        return_value=APIKeyManagerMock(token))
    mocker.patch('cartoframes.viz.kuviz._get_kuviz_manager')
    mocker.patch('cartoframes.viz.kuviz._create_auth_client')
    mocker.patch.object(ContextManager, 'compute_query')
    mocker.patch.object(ContextManager, 'get_schema')
    mocker.patch.object(ContextManager, 'get_table_names')
    mocker.patch.object(ContextManager, 'is_public', return_value=is_public)
    mocker.patch.object(ContextManager, 'get_geom_type', return_value='point')
    mocker.patch.object(ContextManager, 'get_bounds', return_value=None)


class TestKuvizPublisher(object):
    def setup_method(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        assert kuviz_dict['id'] is not None
        assert kuviz_dict['url'] is not None
        assert kuviz_dict['name'] == name
        assert kuviz_dict['privacy'] == privacy

    def test_kuviz_publisher_instantiation(self, mocker):
        setup_mocks(mocker, self.credentials)

        kuviz_publisher = KuvizPublisher(None)

        assert isinstance(kuviz_publisher, KuvizPublisher)
        assert kuviz_publisher._layers == []

    def test_kuviz_publisher_set_layers(self, mocker):
        setup_mocks(mocker, self.credentials)

        source_1 = Source(build_geodataframe([-10, 0], [-10, 0]))
        source_2 = Source(build_geodataframe([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        vmap = Map([
            layer_1,
            layer_2
        ])

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)

        assert kuviz_publisher._layers != vmap.layers
        assert len(kuviz_publisher._layers) == len(vmap.layers)

    def test_kuviz_publisher_use_custom_api_key(self, mocker):
        setup_mocks(mocker, self.credentials)

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers, 'fake_api_key')

        layers = kuviz_publisher.get_layers()

        assert layers[0].source.credentials == self.credentials
        assert layers[0].credentials == ({
            'username': self.username,
            'api_key': 'fake_api_key',
            'base_url': 'https://{}.carto.com'.format(self.username)})

    def test_kuviz_publisher_use_only_base_url(self, mocker):
        credentials = Credentials(base_url='https://fakeuser.carto.com')
        setup_mocks(mocker, credentials)

        vmap = Map(Layer('fake_table', credentials=credentials))

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)

        layers = kuviz_publisher.get_layers()

        assert layers[0].source.credentials == credentials
        assert layers[0].credentials == ({
            'username': 'user',  # Default VL username
            'api_key': DEFAULT_PUBLIC,
            'base_url': 'https://fakeuser.carto.com'})

    def test_kuviz_publisher_create_new_apikey(self, mocker):
        token = '1234'
        setup_mocks(mocker, self.credentials, is_public=False, token=token)

        layers = [Layer('fake_table', credentials=self.credentials)]

        kuviz_publisher = KuvizPublisher(None)

        assert kuviz_publisher._create_maps_api_keys(layers) == token

    def test_kuviz_publisher_publish(self, mocker):
        setup_mocks(mocker, self.credentials)

        kuviz = CartoKuvizMock('fake_kuviz')
        mocker.patch('cartoframes.viz.kuviz._create_kuviz', return_value=kuviz)

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)
        result = kuviz_publisher.publish(html, kuviz_name, None)

        assert kuviz_publisher.kuviz == kuviz
        assert result == kuviz_to_dict(kuviz)

    def test_kuviz_publisher_update_fail(self, mocker):
        setup_mocks(mocker, self.credentials)

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)

        with pytest.raises(Exception):
            kuviz_publisher.update(html, kuviz_name, None)

    def test_kuviz_publisher_update(self, mocker):
        setup_mocks(mocker, self.credentials)

        kuviz = CartoKuvizMock('fake_kuviz')
        mocker.patch('cartoframes.viz.kuviz._create_kuviz', return_value=kuviz)

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)
        result_publish = kuviz_publisher.publish(html, kuviz_name, None)

        kuviz.name = 'fake_name_2'
        result_update = kuviz_publisher.update(html, kuviz_name, None)

        assert kuviz_publisher.kuviz == kuviz
        assert result_update == kuviz_to_dict(kuviz)
        assert result_publish != kuviz_to_dict(kuviz)

    def test_kuviz_publisher_delete(self, mocker):
        setup_mocks(mocker, self.credentials)

        kuviz = CartoKuvizMock('fake_kuviz')
        mocker.patch('cartoframes.viz.kuviz._create_kuviz', return_value=kuviz)

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        html = 'fake_html'
        kuviz_name = 'fake_name'

        kuviz_publisher = KuvizPublisher(None)
        kuviz_publisher.set_layers(vmap.layers)
        kuviz_publisher.publish(html, kuviz_name, None)

        kuviz_publisher.delete()

        assert kuviz_publisher.kuviz is None

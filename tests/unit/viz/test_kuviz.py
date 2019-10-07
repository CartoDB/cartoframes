# -*- coding: utf-8 -*-

from cartoframes.viz import Map, Layer, Source
from cartoframes.data import StrategiesRegistry
from cartoframes.auth import Credentials

from tests.unit.mocks import mock_dataset, mock_kuviz
from tests.unit.mocks.kuviz_mock import KuvizPublisherMock, PRIVACY_PUBLIC, PRIVACY_PASSWORD

from .utils import build_geojson


class TestKuviz(object):
    def setup_method(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

        self.html = '<html><body><h1>Hi Kuviz yeee</h1></body></html>'

    def teardown_method(self):
        StrategiesRegistry.instance = None

    def test_kuviz_create(self, mocker):
        name = 'test-name'
        kuviz = mock_kuviz(name, self.html, self.credentials)
        assert kuviz.id is not None
        assert kuviz.url is not None
        assert kuviz.name == name
        assert kuviz.privacy == PRIVACY_PUBLIC

    def test_kuviz_create_with_password(self):
        name = 'test-name'
        kuviz = mock_kuviz(name, self.html, self.credentials, password="1234")
        assert kuviz.id is not None
        assert kuviz.url is not None
        assert kuviz.name == name
        assert kuviz.privacy == PRIVACY_PASSWORD


class TestKuvizPublisher(object):
    def setup_method(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

    def teardown_method(self):
        StrategiesRegistry.instance = None

    def test_kuviz_publisher_create_local(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        source_2 = Source(build_geojson([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        vmap = Map([
            layer_1,
            layer_2
        ])

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert kuviz_pub._layers != vmap.layers
        assert len(kuviz_pub._layers) == len(vmap.layers)

    def test_kuviz_publisher_has_layers_copy(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert len(kuviz_pub._layers) == len(vmap.layers)

        kuviz_pub._layers = []
        assert len(kuviz_pub._layers) != len(vmap.layers)

    def test_kuviz_publisher_from_local_sync(self):
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer_1 = Layer(source_1)
        vmap = Map(layer_1)

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert kuviz_pub.is_sync() is False

    def test_kuviz_publisher_create_remote(self, mocker):
        dataset = mock_dataset(mocker, 'fake_table', self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert kuviz_pub._layers != vmap.layers
        assert len(kuviz_pub._layers) == len(vmap.layers)

    def test_kuviz_publisher_create_remote_sync(self, mocker):
        dataset = mock_dataset(mocker, 'fake_table', self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert kuviz_pub.is_sync() is True

    def test_kuviz_publisher_unsync(self, mocker):
        dataset = mock_dataset(mocker, build_geojson([-10, 0], [-10, 0]))
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        assert kuviz_pub.is_sync() is False

    def test_kuviz_publisher_sync_layers(self, mocker):
        dataset = mock_dataset(mocker, build_geojson([-10, 0], [-10, 0]))
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        kuviz_pub.sync_layers(table_name='fake_table', credentials=self.credentials)
        assert kuviz_pub.is_sync() is True

    def test_kuviz_publisher_get_layers_defaul_apikey(self, mocker):
        dataset = mock_dataset(mocker, 'fake_table', self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        kuviz_pub.set_credentials(self.credentials)
        layers = kuviz_pub.get_layers()

        assert layers[0].source.dataset.credentials == self.credentials
        assert layers[0].credentials == {
            'username': self.username,
            'api_key': 'default_public',
            'base_url': 'https://{}.carto.com'.format(self.username)}

    def test_kuviz_publisher_get_layers_with_api_key(self, mocker):
        dataset = mock_dataset(mocker, 'fake_table', self.credentials)
        vmap = Map(Layer(Source(dataset)))

        kuviz_pub = KuvizPublisherMock(vmap.layers)
        kuviz_pub.set_credentials(self.credentials)
        maps_api_key = '1234'
        layers = kuviz_pub.get_layers(maps_api_key=maps_api_key)

        assert layers[0].source.dataset.credentials == self.credentials
        assert layers[0].credentials == {
            'username': self.username,
            'api_key': maps_api_key,
            'base_url': 'https://{}.carto.com'.format(self.username)}

    def test_kuviz_publisher_all(self):
        kuviz_dicts = KuvizPublisherMock.all()
        for kuviz_dict in kuviz_dicts:
            self.assert_kuviz_dict(kuviz_dict, name='test', privacy=PRIVACY_PUBLIC)

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        assert kuviz_dict['id'] is not None
        assert kuviz_dict['url'] is not None
        assert kuviz_dict['name'] == name
        assert kuviz_dict['privacy'] == privacy

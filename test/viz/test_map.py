import unittest

from carto.exceptions import CartoException

from cartoframes import context
from cartoframes.viz import Map, Layer, Source, constants
from cartoframes.data import StrategiesRegistry
from cartoframes.auth import Credentials

from ..mocks.map_mock import MapMock
from ..mocks.dataset_mock import DatasetMock
from ..mocks.context_mock import ContextMock
from ..mocks.kuviz_mock import KuvizPublisherMock, PRIVACY_PUBLIC, PRIVACY_PASSWORD

from .utils import build_geojson


class TestMap(unittest.TestCase):
    def test_is_defined(self):
        """Map"""
        self.assertNotEqual(Map, None)


class TestMapInitialization(unittest.TestCase):
    def test_size(self):
        """Map should set the size by default"""
        map = Map()
        self.assertIsNone(map.size)

    def test__init(self):
        """Map should return a valid template"""
        map = Map()
        self.assertIsNotNone(map._htmlMap)

    def test_bounds(self):
        """Map should set the bounds"""
        map = Map(bounds={
            'west': -10,
            'east': 10,
            'north': -10,
            'south': 10
        })
        self.assertEqual(map.bounds, [[-10, 10], [10, -10]])

    def test_bounds_clamp(self):
        """Map should set the bounds clamped"""
        map = Map(bounds={
            'west': -1000,
            'east': 1000,
            'north': -1000,
            'south': 1000
        })
        self.assertEqual(map.bounds, [[-180, 90], [180, -90]])


class TestMapLayer(unittest.TestCase):
    def test_one_layer(self):
        """Map layer should be able to initialize one layer"""
        source = Source(build_geojson([-10, 0], [-10, 0]))
        layer = Layer(source)
        map = Map(layer)

        self.assertEqual(map.layers, [layer])
        self.assertEqual(len(map.layer_defs), 1)
        self.assertEqual(map.layer_defs[0].get('interactivity'), [])
        self.assertIsNotNone(map.layer_defs[0].get('credentials'))
        self.assertIsNotNone(map.layer_defs[0].get('legend'))
        self.assertIsNotNone(map.layer_defs[0].get('query'))
        self.assertEqual(map.layer_defs[0].get('type'), 'GeoJSON')
        self.assertIsNotNone(map.layer_defs[0].get('viz'))

    def test_two_layers(self):
        """Map layer should be able to initialize two layers in the correct order"""
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        source_2 = Source(build_geojson([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        map = Map([
            layer_1,
            layer_2
        ])

        self.assertEqual(map.layers, [
            layer_1,
            layer_2
        ])
        self.assertEqual(len(map.layer_defs), 2)

    def test_interactive_layer(self):
        """Map layer should indicate if the layer has interactivity configured"""
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer = Layer(
            source_1,
            popup={
                'click': ['$pop', '$name'],
                'hover': [{
                    'title': 'Pop',
                    'value': '$pop'
                }]
            }
        )

        map = Map(layer)
        self.assertEqual(map.layer_defs[0].get('interactivity'), [{
            'event': 'click',
            'attrs': [{
                'name': 'v559339',
                'title': '$pop'
            }, {
                'name': 'v8e0f74',
                'title': '$name'
            }]
        }, {
            'event': 'hover',
            'attrs': [{
                'name': 'v559339',
                'title': 'Pop'
            }]
        }])

    def test_default_interactive_layer(self):
        """Map layer should get the default event if the interactivity is set to []"""
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer = Layer(
            source_1,
            popup={}
        )

        map = Map(layer)
        self.assertEqual(map.layer_defs[0].get('interactivity'), [])


class TestMapDevelopmentPath(unittest.TestCase):
    def test_default_carto_vl_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        template = map._htmlMap.html
        self.assertTrue(constants.CARTO_VL_URL in template)

    def test_custom_carto_vl_path(self):
        """Map dev path should use custom paths"""
        _carto_vl_path = 'custom_carto_vl_path'
        map = Map(_carto_vl_path=_carto_vl_path)
        template = map._htmlMap.html
        self.assertTrue(_carto_vl_path + constants.CARTO_VL_DEV in template)

    def test_default_airship_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        template = map._htmlMap.html
        self.assertTrue(constants.AIRSHIP_COMPONENTS_URL in template)
        self.assertTrue(constants.AIRSHIP_BRIDGE_URL in template)
        self.assertTrue(constants.AIRSHIP_STYLES_URL in template)
        self.assertTrue(constants.AIRSHIP_MODULE_URL in template)
        self.assertTrue(constants.AIRSHIP_ICONS_URL in template)

    def test_custom_airship_path(self):
        """Map dev path should use custom paths"""
        _airship_path = 'custom_airship_path'
        map = Map(_airship_path=_airship_path)
        template = map._htmlMap.html
        self.assertTrue(_airship_path + constants.AIRSHIP_COMPONENTS_DEV in template)
        self.assertTrue(_airship_path + constants.AIRSHIP_BRIDGE_DEV in template)
        self.assertTrue(_airship_path + constants.AIRSHIP_STYLES_DEV in template)
        self.assertTrue(_airship_path + constants.AIRSHIP_MODULE_DEV in template)
        self.assertTrue(_airship_path + constants.AIRSHIP_ICONS_DEV in template)


class TestMapPublication(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)
        self._context_mock = ContextMock()

        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock

        self.html = "<html><body><h1>Hi Kuviz yeee</h1></body></html>"

    def tearDown(self):
        context.create_context = self.original_create_context
        StrategiesRegistry.instance = None

    def assert_kuviz(self, kuviz, name, privacy):
        self.assertIsNotNone(kuviz.id)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, privacy)

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        self.assertIsNotNone(kuviz_dict['id'])
        self.assertIsNotNone(kuviz_dict['url'])
        self.assertEqual(kuviz_dict['name'], name)
        self.assertEqual(kuviz_dict['privacy'], privacy)

    def test_map_publish_remote(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        name = 'cf_publish'
        kuviz_dict = map.publish(name, credentials=self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, PRIVACY_PUBLIC)
        self.assert_kuviz(map._kuviz, name, PRIVACY_PUBLIC)

    def test_map_publish_unsync_fails(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset._is_saved_in_carto = False
        map = MapMock(Layer(Source(dataset)))

        msg = 'The map layers are not synchronized with CARTO. Please, use the `sync_data` before publishing the map'
        with self.assertRaises(CartoException, msg=msg):
            map.publish('test', credentials=self.credentials)

    def test_map_publish_unsync_sync_data_and_publish(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.credentials)
        dataset._is_saved_in_carto = False
        map = MapMock(Layer(Source(dataset)))

        map.sync_data(table_name='fake_table', credentials=self.credentials)

        name = 'cf_publish'
        kuviz_dict = map.publish(name, credentials=self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, PRIVACY_PUBLIC)
        self.assert_kuviz(map._kuviz, name, PRIVACY_PUBLIC)

    def test_map_publish_with_password(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        name = 'cf_publish'
        kuviz_dict = map.publish(name, credentials=self.credentials, password="1234")
        self.assert_kuviz_dict(kuviz_dict, name, PRIVACY_PASSWORD)
        self.assert_kuviz(map._kuviz, name, PRIVACY_PASSWORD)

    def test_map_publish_deletion(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        name = 'cf_publish'
        map.publish(name, credentials=self.credentials)
        map.delete_publication()
        self.assertIsNone(map._kuviz)

    def test_map_publish_update_name(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        name = 'cf_publish'
        map.publish(name, credentials=self.credentials)
        new_name = 'cf_update'
        kuviz_dict = map.update_publication(new_name, password=None)
        self.assert_kuviz_dict(kuviz_dict, new_name, PRIVACY_PUBLIC)
        self.assert_kuviz(map._kuviz, new_name, PRIVACY_PUBLIC)

    def test_map_publish_update_password(self):
        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        name = 'cf_publish'
        map.publish(name, credentials=self.credentials)
        kuviz_dict = map.update_publication(name, password="1234")
        self.assert_kuviz_dict(kuviz_dict, name, PRIVACY_PASSWORD)
        self.assert_kuviz(map._kuviz, name, PRIVACY_PASSWORD)

    def test_map_publish_private_ds_with_public_apikey_fails(self):
        is_public = KuvizPublisherMock.is_public

        def is_not_public(self):
            return False

        KuvizPublisherMock.is_public = is_not_public

        dataset = DatasetMock('fake_table', credentials=self.credentials)
        map = MapMock(Layer(Source(dataset)))

        msg = ('The datasets used in your map are not public. '
               'You need add new Regular API key with permissions to Maps API and the datasets. '
               'You can do it from your CARTO dashboard or using the Auth API. You can get more '
               'info at https://carto.com/developers/auth-api/guides/types-of-API-Keys/')
        with self.assertRaises(CartoException, msg=msg):
            map.publish('test', credentials=self.credentials)

        KuvizPublisherMock.is_public = is_public

import unittest
from cartoframes.viz import Map, Layer, Source, defaults
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


class TestMapLayer(unittest.TestCase):
    def test_one_layer(self):
        """Map layer should be able to initialize one layer"""
        source = Source(build_geojson([-10, 0], [-10, 0]))
        layer = Layer(source)
        map = Map(layer)

        self.assertEqual(map.layers, [layer])
        self.assertEqual(len(map.sources), 1)
        self.assertEqual(map.sources[0].get('interactivity'), [])
        self.assertIsNotNone(map.sources[0].get('credentials'))
        self.assertIsNone(map.sources[0].get('legend'))
        self.assertIsNotNone(map.sources[0].get('query'))
        self.assertEqual(map.sources[0].get('type'), 'GeoJSON')
        self.assertIsNotNone(map.sources[0].get('viz'))

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
            layer_2,
            layer_1
        ])
        self.assertEqual(len(map.sources), 2)

    def test_interactive_layer(self):
        """Map layer should indicate if the layer has interactivity configured"""
        source_1 = Source(build_geojson([-10, 0], [-10, 0]))
        layer = Layer(
            source_1,
            popup={
                'click': ['$pop', '$name'],
                'hover': [{
                    'label': 'Pop',
                    'value': '$pop'
                }]
            }
        )

        map = Map(layer)
        self.assertEqual(map.sources[0].get('interactivity'), [{
            'event': 'click',
            'attrs': [{
                'name': 'v559339',
                'label': '$pop'
            }, {
                'name': 'v8e0f74',
                'label': '$name'
            }]
        }, {
            'event': 'hover',
            'attrs': [{
                'name': 'v559339',
                'label': 'Pop'
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
        self.assertEqual(map.sources[0].get('interactivity'), [])


class TestMapDevelopmentPath(unittest.TestCase):
    def test_default_carto_vl_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        template = map._htmlMap.html
        self.assertTrue(defaults.CARTO_VL_PATH in template)

    def test_custom_carto_vl_path(self):
        """Map dev path should use custom paths"""
        _carto_vl_path = 'custom_carto_vl_path'
        map = Map(_carto_vl_path=_carto_vl_path)
        template = map._htmlMap.html
        self.assertTrue(_carto_vl_path in template)

    def test_default_airship_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        template = map._htmlMap.html
        self.assertTrue(defaults.AIRSHIP_COMPONENTS_PATH in template)
        self.assertTrue(defaults.AIRSHIP_BRIDGE_PATH in template)
        self.assertTrue(defaults.AIRSHIP_STYLES_PATH in template)
        self.assertTrue(defaults.AIRSHIP_ICONS_PATH in template)

    def test_custom_airship_path(self):
        """Map dev path should use custom paths"""
        _airship_path = 'custom_airship_path'
        map = Map(_airship_path=_airship_path)
        template = map._htmlMap.html
        self.assertTrue(_airship_path + defaults.AIRSHIP_COMPONENTS in template)
        self.assertTrue(_airship_path + defaults.AIRSHIP_BRIDGE in template)
        self.assertTrue(_airship_path + defaults.AIRSHIP_STYLE in template)
        self.assertTrue(_airship_path + defaults.AIRSHIP_ICONS in template)

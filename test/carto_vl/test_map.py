import unittest
from pandas import DataFrame
from geopandas import GeoDataFrame
from cartoframes import carto_vl
from shapely.geometry import Point
from cartoframes.carto_vl import defaults


class TestMap(unittest.TestCase):
    def test_is_defined(self):
        self.assertNotEqual(carto_vl.Map, None)


class TestMapInitialization(unittest.TestCase):
    def test_size(self):
        """should set the size by default"""
        carto_vl_map = carto_vl.Map()
        self.assertIsNone(carto_vl_map.size)

    def test__init(self):
        """should return a valid template"""
        carto_vl_map = carto_vl.Map()
        self.assertIsNotNone(carto_vl_map._htmlMap)


class TestMapLocalLayers(unittest.TestCase):
    def test_one_layer(self):
        """should be able to initialize one local layer"""
        layer_1 = _build_local_source([-10, 0], [-10, 0])
        carto_vl_local_layer = carto_vl.LocalLayer(layer_1)
        carto_vl_map = carto_vl.Map(carto_vl_local_layer)

        self.assertEqual(carto_vl_map.layers, [carto_vl_local_layer])
        self.assertEqual(len(carto_vl_map.sources), 1)
        self.assertFalse(carto_vl_map.sources[0].get('interactivity'))
        self.assertTrue(carto_vl_map.sources[0].get('is_local'))
        self.assertIsNone(carto_vl_map.sources[0].get('legend'))
        self.assertIsNotNone(carto_vl_map.sources[0].get('source'))
        self.assertIsNotNone(carto_vl_map.sources[0].get('viz'))

    def test_two_layers(self):
        """should be able to initialize two local layer in the correct order"""
        layer_1 = _build_local_source([-10, 0], [-10, 0])
        layer_2 = _build_local_source([0, 10], [10, 0])
        carto_vl_local_layer_1 = carto_vl.Layer(layer_1)
        carto_vl_local_layer_2 = carto_vl.Layer(layer_2)
        carto_vl_map = carto_vl.Map([
            carto_vl_local_layer_1,
            carto_vl_local_layer_2
        ])

        self.assertEqual(carto_vl_map.layers, [
            carto_vl_local_layer_2,
            carto_vl_local_layer_1,
        ])
        self.assertEqual(len(carto_vl_map.sources), 2)

    def test_interactive_layer(self):
        """should indicate if the layer has interactivity enabled"""
        layer_1 = _build_local_source([-10, 0], [-10, 0])
        interactivity = {'event': 'click'}
        carto_vl_local_layer = carto_vl.LocalLayer(
            layer_1,
            interactivity=interactivity
        )

        carto_vl_map = carto_vl.Map(carto_vl_local_layer)
        self.assertTrue(carto_vl_map.sources[0].get('interactivity'))

    def test_default_interactive_layer(self):
        """should get the default event if the interactivity is set to True"""
        layer_1 = _build_local_source([-10, 0], [-10, 0])
        interactivity = True
        carto_vl_local_layer = carto_vl.LocalLayer(
            layer_1,
            interactivity=interactivity
        )

        carto_vl_map = carto_vl.Map(carto_vl_local_layer)
        layer_interactivity = carto_vl_map.sources[0].get('interactivity')
        self.assertTrue(layer_interactivity)
        self.assertEqual(layer_interactivity.get('event'), 'hover')


class TestMapDevelopmentPath(unittest.TestCase):
    def test_default_carto_vl_path(self):
        """should use default paths if none are given"""
        carto_vl_map = carto_vl.Map()
        template = carto_vl_map._htmlMap.html
        self.assertTrue(defaults._CARTO_VL_PATH in template)

    def test_custom_carto_vl_path(self):
        """should use custom paths"""
        _carto_vl_path = 'custom_carto_vl_path'
        carto_vl_map = carto_vl.Map(_carto_vl_path=_carto_vl_path)
        template = carto_vl_map._htmlMap.html
        self.assertTrue(_carto_vl_path in template)

    def test_default_airship_path(self):
        """should use default paths if none are given"""
        carto_vl_map = carto_vl.Map()
        template = carto_vl_map._htmlMap.html
        self.assertTrue(defaults._AIRSHIP_COMPONENTS_PATH in template)
        self.assertTrue(defaults._AIRSHIP_BRIDGE_PATH in template)
        self.assertTrue(defaults._AIRSHIP_STYLES_PATH in template)
        self.assertTrue(defaults._AIRSHIP_ICONS_PATH in template)

    def test_custom_airship_path(self):
        """should use custom paths"""
        _airship_path = 'custom_airship_path'
        carto_vl_map = carto_vl.Map(_airship_path=_airship_path)
        template = carto_vl_map._htmlMap.html
        self.assertTrue(_airship_path + defaults._AIRSHIP_SCRIPT in template)
        self.assertTrue(_airship_path + defaults._AIRSHIP_BRIDGE_SCRIPT in template)
        self.assertTrue(_airship_path + defaults._AIRSHIP_STYLE in template)
        self.assertTrue(_airship_path + defaults._AIRSHIP_ICONS_STYLE in template)


def _build_local_source(lats, lngs):
    coordinates = {
        'Latitude': lats,
        'Longitude': lngs
    }

    dataframe = DataFrame(coordinates)
    dataframe['Coordinates'] = list(zip(dataframe.Longitude, dataframe.Latitude))
    dataframe['Coordinates'] = dataframe['Coordinates'].apply(Point)

    return GeoDataFrame(dataframe, geometry='Coordinates')

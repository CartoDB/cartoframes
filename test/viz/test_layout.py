import unittest

from carto.exceptions import CartoException
from cartoframes.viz import Map, Layout, Layer, Source

from .utils import build_geojson

source = build_geojson([-10, 0], [-10, 0])


class TestLayout(unittest.TestCase):
    def test_is_defined(self):
        """Layout"""
        self.assertNotEqual(Layout, None)


class TestLayoutInitialization(unittest.TestCase):
    def test__init(self):
        """Layout should init properly"""
        layout = Layout([])
        self.assertIsNotNone(layout._layout)
        self.assertEqual(layout._N_SIZE, 0)
        self.assertEqual(layout._M_SIZE, 1)
        self.assertIsNone(layout._viewport)
        self.assertTrue(layout._is_static)

    def test__init_maps(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(source))), Map(Layer(Source(source)))])
        self.assertEqual(layout._N_SIZE, 2)
        self.assertEqual(layout._M_SIZE, 1)

    def test__init_maps_valid(self):
        """Layout should raise an error if any element in the map list is not a Map"""

        msg = 'All the elements in the Layout should be an instance of Map'
        with self.assertRaises(CartoException, msg=msg):
            Layout([Layer(Source(source))])

    def test__init_maps_size(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(source))), Map(Layer(Source(source)))], 1, 2)
        self.assertEqual(layout._N_SIZE, 1)
        self.assertEqual(layout._M_SIZE, 2)


class TestLayoutSettings(unittest.TestCase):
    def test_global_viewport(self):
        """Layout should return the same viewport for every map"""
        layout = Layout([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(layout._layout[0].get('viewport'), {'zoom': 5})
        self.assertEqual(layout._layout[1].get('viewport'), {'zoom': 5})

    def test_custom_viewport(self):
        """Layout should return a different viewport for every map"""
        layout = Layout([
            Map(Layer(Source(source)), viewport={'zoom': 2}),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(layout._layout[0].get('viewport'), {'zoom': 2})
        self.assertEqual(layout._layout[1].get('viewport'), {'zoom': 5})

    def test_global_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(layout._layout[0].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})
        self.assertEqual(layout._layout[1].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})

    def test_custom_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(source)), viewport={'zoom': 2}),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(layout._layout[0].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 2})
        self.assertEqual(layout._layout[1].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})

    def test_is_static(self):
        """Layout should set correctly is_static property for each map"""
        layout = Layout([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertTrue(layout._layout[0].get('is_static'))
        self.assertTrue(layout._layout[1].get('is_static'))

import unittest

from carto.exceptions import CartoException
from cartoframes.viz import Map, MapGrid, Layer, Source

from .utils import build_geojson

source = build_geojson([-10, 0], [-10, 0])


class TestMapGrid(unittest.TestCase):
    def test_is_defined(self):
        """MapGrid"""
        self.assertNotEqual(MapGrid, None)


class TestMapGridInitialization(unittest.TestCase):
    def test__init(self):
        """MapGrid should init properly"""
        mapgrid = MapGrid([])
        self.assertIsNotNone(mapgrid._map_grid)
        self.assertEqual(mapgrid._N_SIZE, 0)
        self.assertEqual(mapgrid._M_SIZE, 1)
        self.assertIsNone(mapgrid._viewport)
        self.assertTrue(mapgrid._is_static)

    def test__init_maps(self):
        """MapGrid should init properly"""
        mapgrid = MapGrid([Map(Layer(Source(source))), Map(Layer(Source(source)))])
        self.assertEqual(mapgrid._N_SIZE, 2)
        self.assertEqual(mapgrid._M_SIZE, 1)

    def test__init_maps_valid(self):
        """MapGrid should raise an error if any element in the map list is not a Map"""

        msg = 'All the elements in the MapGrid should be an instance of Map'
        with self.assertRaises(CartoException, msg=msg):
            MapGrid([Layer(Source(source))])

    def test__init_maps_size(self):
        """MapGrid should init properly"""
        mapgrid = MapGrid([Map(Layer(Source(source))), Map(Layer(Source(source)))], 1, 2)
        self.assertEqual(mapgrid._N_SIZE, 1)
        self.assertEqual(mapgrid._M_SIZE, 2)


class TestMapGridSettings(unittest.TestCase):
    def test_global_viewport(self):
        """MapGrid should return the same viewport for every map"""
        mapgrid = MapGrid([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(mapgrid._map_grid[0].get('viewport'), {'zoom': 5})
        self.assertEqual(mapgrid._map_grid[1].get('viewport'), {'zoom': 5})

    def test_custom_viewport(self):
        """MapGrid should return a different viewport for every map"""
        mapgrid = MapGrid([
            Map(Layer(Source(source)), viewport={'zoom': 2}),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(mapgrid._map_grid[0].get('viewport'), {'zoom': 2})
        self.assertEqual(mapgrid._map_grid[1].get('viewport'), {'zoom': 5})

    def test_global_camera(self):
        """MapGrid should return the correct camera for each map"""
        mapgrid = MapGrid([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(mapgrid._map_grid[0].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})
        self.assertEqual(mapgrid._map_grid[1].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})

    def test_custom_camera(self):
        """MapGrid should return the correct camera for each map"""
        mapgrid = MapGrid([
            Map(Layer(Source(source)), viewport={'zoom': 2}),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertEqual(mapgrid._map_grid[0].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 2})
        self.assertEqual(mapgrid._map_grid[1].get('camera'),
                         {'bearing': None, 'center': None, 'pitch': None, 'zoom': 5})

    def test_is_static(self):
        """MapGrid should set correctly is_static property for each map"""
        mapgrid = MapGrid([
            Map(Layer(Source(source))),
            Map(Layer(Source(source)))],
            viewport={'zoom': 5})

        self.assertTrue(mapgrid._map_grid[0].get('is_static'))
        self.assertTrue(mapgrid._map_grid[1].get('is_static'))

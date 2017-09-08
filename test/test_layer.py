"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, QueryLayer
from cartoframes import styling


class TestBaseMap(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        # basemaps with baked-in labels
        self.dark_map_all = BaseMap(source='dark')
        self.light_map_all = BaseMap(source='light')

        # basemaps with no labels
        self.dark_map_no_labels = BaseMap(source='dark',
                                          labels=None)
        self.light_map_no_labels = BaseMap(source='light',
                                           labels=None)

        # labels with no basemaps
        self.dark_only_labels = BaseMap(source='dark',
                                        only_labels=True)
        self.light_only_labels = BaseMap(source='light',
                                         only_labels=True)

    def test_basemap_invalid(self):
        """layer.Basemap exceptions on invalid source"""
        # Raise ValueError if invalid label is entered
        with self.assertRaises(ValueError):
            BaseMap(labels='watermelon')

        # Raise ValueError if custom URL is entered
        with self.assertRaises(ValueError):
            BaseMap(source='http://spinalmap.com/{z}/{x}/{y}.png')

        # Raise ValueError if non-supported style type is entered
        with self.assertRaises(ValueError):
            BaseMap(source='gulab_jamon')

    def test_basemap_source(self):
        """layer.BaseMap with different sources and labels"""

        # ensure correct BaseMap urls are created
        # See URLs here: https://carto.com/location-data-services/basemaps/
        self.assertEqual(self.dark_map_all.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_all/{z}/{x}/{y}.png')
        self.assertEqual(self.light_map_all.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_all/{z}/{x}/{y}.png')
        self.assertEqual(self.dark_map_no_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(self.light_map_no_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(self.light_only_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_only_labels/{z}/{x}/{y}.png')
        self.assertEqual(self.dark_only_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_only_labels/{z}/{x}/{y}.png')

        # ensure self.is_basic() works as intended
        self.assertTrue(self.light_map_all.is_basic(),
                        msg='is a basic carto basemap')
        self.assertTrue(self.dark_map_all.is_basic())


class TestQueryLayer(unittest.TestCase):
    """Tests for functions in QueryLayer module"""
    def setUp(self):
        self.query = 'select * from watermelon'

    def test_querylayer_colors(self):
        """layer.QueryLayer color options tests"""

        # no color options passed
        basic = QueryLayer(self.query)
        self.assertEqual(basic.color, None)

        # check valid dict color options
        dict_colors = [{'column': 'mandrill', 'scheme': styling.armyRose(7)},
                       {'column': 'mercxx', 'scheme': {'bin_method': 'equal',
                                                       'bins': 7,
                                                       'name': 'Temps'}},
                       {'column': 'elephant',
                        'scheme': styling.redOr(10, bin_method='jenks')}]
        dict_colors_ans = ['mandrill', 'mercxx', 'elephant']
        dict_colors_scheme = [{'name': 'ArmyRose',
                               'bins': 7,
                               'bin_method': 'quantiles'},
                              {'name': 'Temps',
                               'bins': 7,
                               'bin_method': 'equal'},
                              {'name': 'RedOr',
                               'bins': 10,
                               'bin_method': 'jenks'}]
        for idx, val in enumerate(dict_colors):
            qlayer = QueryLayer(self.query, color=val)
            self.assertEqual(qlayer.color, dict_colors_ans[idx])
            self.assertEqual(qlayer.scheme, dict_colors_scheme[idx])

        # check valid string color options
        str_colors = ['#FF0000', 'aliceblue', 'cookie_monster']
        str_colors_ans = ['#FF0000', 'aliceblue', 'cookie_monster']
        str_scheme_ans = [None, None, styling.mint(5)]

        for idx, color in enumerate(str_colors):
            qlayer = QueryLayer(self.query, color=color)
            print(qlayer.color)
            self.assertEqual(qlayer.color, str_colors_ans[idx])
            self.assertEqual(qlayer.scheme, str_scheme_ans[idx])

        # Exception testing
        # color column cannot be a geometry column
        with self.assertRaises(ValueError,
                               msg='color clumn cannot be a geometry column'):
            QueryLayer(self.query, color='the_geom')

        # color dict must have a 'column' key
        with self.assertRaises(ValueError,
                               msg='color dict must have a `column` key'):
            QueryLayer(self.query, color={'scheme': styling.vivid(10)})

    def test_querylayer_time_errors(self):
        """layer.QueryLayer time option exceptions"""

        # time str column cannot be the_geom
        with self.assertRaises(ValueError,
                               msg='time column cannot be `the_geom`'):
            QueryLayer(self.query, time='the_geom')

        # time dict must have a 'column' key
        with self.assertRaises(ValueError,
                               msg='time dict must have a `column` key'):
            QueryLayer(self.query, time={'scheme': styling.armyRose(10)})

        # pass an int as the time column
        with self.assertRaises(ValueError,
                               msg='`time` key has to be a str or dict'):
            QueryLayer(self.query, time=7)

    def test_querylayer_time_default(self):
        """layer.QueryLayer time defaults"""
        time_ans = {'column': 'time_col',
                    'method': 'count',
                    'cumulative': False,
                    'frames': 256,
                    'duration': 30}
        # pass a valid column name
        qlayer = QueryLayer(self.query, time='time_col')
        self.assertEqual(qlayer.time, time_ans)

        # pass a valid dict style
        qlayer = QueryLayer(self.query, time={'column': 'time_col',
                                              'method': 'avg',
                                              'duration': 10})
        time_ans = {'column': 'time_col',
                    'method': 'avg',
                    'frames': 256,
                    'duration': 10,
                    'cumulative': False}

        self.assertEqual(qlayer.time, time_ans)

    def test_querylayer_size_column_key(self):
        """layer.QueryLayer size dict has to have a column key"""

        # size dict must have a 'column' key
        with self.assertRaises(ValueError,
                               msg='size dict must have a `column` key'):
            QueryLayer(self.query, size={'scheme': styling.temps(10)})

    def test_querylayer_size_and_time(self):
        """layer.QueryLayer size and time cannot be used together"""
        # size and time cannot be specified at the same time if size is
        #  styled by value
        with self.assertRaises(ValueError,
                               msg='time key should not be present'):
            QueryLayer(self.query,
                       size={'column': 'mag',
                             'scheme': styling.temps(10)},
                       time='date_col')

    def test_querylayer_size_default(self):
        """layer.QueryLayer size to have default value"""
        qlayer = QueryLayer(self.query)
        self.assertEqual(qlayer.size, 10,
                         msg='should return default styling of 10')

    def test_querylayer_size_defaults(self):
        """layer.QueryLayer gets defaults for options not passed"""
        qlayer = QueryLayer(self.query, size='cold_brew')
        size_col_ans = {'column': 'cold_brew',
                        'range': [5, 25],
                        'bins': 10,
                        'bin_method': 'quantiles'}
        self.assertEqual(qlayer.size, size_col_ans,
                         msg='size column should receive defaults')

        qlayer = QueryLayer(self.query, size={'column': 'cold_brew',
                                              'range': [4, 15],
                                              'bin_method': 'equal'})
        ans = {'column': 'cold_brew',
               'range': [4, 15],
               'bins': 10,
               'bin_method': 'equal'}
        self.assertEqual(qlayer.size, ans,
                         msg=('size dict should receive defaults if not '
                              'provided'))

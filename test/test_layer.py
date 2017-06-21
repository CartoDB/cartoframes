"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, Layer, QueryLayer
from cartoframes import styling

class TestBaseMap(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        pass

    def test_basemap_source(self):
        """Create basemap instances with different sources and labels"""
        # basemaps with baked-in labels
        dark_map_all = BaseMap(source='dark')
        light_map_all = BaseMap(source='light')

        # basemaps with no labels
        dark_map_no_labels = BaseMap(source='dark',
                                     labels=None)
        light_map_no_labels = BaseMap(source='light',
                                      labels=None)
        # labels with no basemaps
        dark_only_labels = BaseMap(source='dark',
                                   only_labels=True)
        light_only_labels = BaseMap(source='light',
                                    only_labels=True)

        # Raise ValueError if invalid label is entered
        with self.assertRaises(ValueError):
            BaseMap(labels='watermelon')

        # Raise ValueError if custom URL is entered
        with self.assertRaises(ValueError):
            BaseMap(source='http://spinalmap.com/{z}/{x}/{y}.png')

        # Raise ValueError if non-supported style type is entered
        with self.assertRaises(ValueError):
            BaseMap(source='gulab_jamon')

        # ensure correct BaseMap urls are created
        # See URLs here: https://carto.com/location-data-services/basemaps/
        self.assertEqual(dark_map_all.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_all/{z}/{x}/{y}.png')
        self.assertEqual(light_map_all.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_all/{z}/{x}/{y}.png')
        self.assertEqual(dark_map_no_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(light_map_no_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(light_only_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'light_only_labels/{z}/{x}/{y}.png')
        self.assertEqual(dark_only_labels.url,
                         'https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                         'dark_only_labels/{z}/{x}/{y}.png')

        # ensure self.is_basic() works as intended
        self.assertTrue(light_map_all.is_basic())
        self.assertTrue(dark_map_all.is_basic())

    def test_querylayer_colors(self):
        """layer.QueryLayer color options tests"""
        query = 'select * from watermelon'

        # no color options passed
        basic = QueryLayer(query)
        self.assertEqual(basic.color, None)

        # check valid dict color options
        dict_colors = [{'column': 'mandrill', 'scheme': styling.armyRose(7)},
                       {'column': 'mercxx', 'scheme': {'bin_method': 'equal',
                                                       'bins': 7,
                                                       'name': 'Temps'}},
                       {'column': 'elephant',
                        'scheme': styling.redOr(10, bin_method='jenks')}]
        dict_colors_ans = ['mandrill', 'mercxx', 'elephant']
        dict_colors_scheme = [{'name': 'ArmyRose', 'bins': 7, 'bin_method': 'quantiles'},
                              {'name': 'Temps', 'bins': 7, 'bin_method': 'equal'},
                              {'name': 'RedOr', 'bins': 10, 'bin_method': 'jenks'}]
        for idx, val in enumerate(dict_colors):
            ql = QueryLayer(query, color=val)
            self.assertEqual(ql.color, dict_colors_ans[idx])
            self.assertEqual(ql.scheme, dict_colors_scheme[idx])

        # check valid string color options
        str_colors = ['#FF0000', 'aliceblue', 'cookie_monster']
        str_colors_ans = ['#FF0000', 'aliceblue', 'cookie_monster']
        str_scheme_ans = [None, None, styling.mint(5)]

        for idx, color in enumerate(str_colors):
            ql = QueryLayer(query, color=color)
            print(ql.color)
            self.assertEqual(ql.color, str_colors_ans[idx])
            self.assertEqual(ql.scheme, str_scheme_ans[idx])

        # Exception testing
        # color column cannot be a geometry column
        with self.assertRaises(ValueError):
            QueryLayer(query, color='the_geom')

        # color dict must have a 'column' key
        with self.assertRaises(ValueError):
            QueryLayer(query, color={'scheme': styling.vivid(10)})

        # time dict cannot be a geometry column
        with self.assertRaises(ValueError):
            QueryLayer(query, time='the_geom')

        # time dict must have a 'column' key
        with self.assertRaises(ValueError):
            QueryLayer(query, time={'scheme': styling.armyRose(10)})

        # size dict must have a 'column' key
        with self.assertRaises(ValueError):
            QueryLayer(query, size={'scheme': styling.temps(10)})

        # size and time cannot be specified at the same time if size is
        #  styled by value
        with self.assertRaises(ValueError, msg='time key should not be present'):
            QueryLayer(query,
                       size={'column': 'mag',
                             'scheme': styling.temps(10)},
                       time='date_col')
        with self.assertRaises(ValueError, msg=('size dict style should '
                                                'contain a `name` key')):
            QueryLayer(query,
                       size={'col': 'mag'})

    def test_querylayer_time(self):
        query = 'select * from watermelon'
        with self.assertRaises(ValueError,
                               msg='`time` key has to be a str or dict'):
            QueryLayer(query, time=7)

        # basic._setup()
    # def test_key_setting(self):
    #     """Test case where API key is valid"""
    #     credentials._remove_creds()
    #     credentials.set_api_key(self.key)
    #     context.CartoContext(base_url=self.base_url)
    #     with self.assertRaises(TypeError):
    #         credentials.set_api_key(self.key, overwrite=False)
    #     credentials.set_api_key(self.key[::-1], overwrite=True)
    #     self.assertEqual(credentials.api_key(), self.key[::-1])


    # def test_base_url_setting(self):
    #     """Test case where API base url is valid"""
    #     credentials._remove_creds()
    #     credentials.set_base_url(self.base_url)
    #     context.CartoContext(api_key=self.key)
    #     with self.assertRaises(TypeError):
    #         credentials.set_base_url(self.base_url, overwrite=False)
    #     credentials.set_base_url(self.base_url[::-1], overwrite=True)
    #     self.assertEqual(credentials.base_url(), self.base_url[::-1])

    # def test_set_credentials(self):
    #     """Test case where API url is valid"""
    #     credentials._remove_creds()
    #     credentials.set_credentials(base_url=self.base_url, api_key=self.key)
    #     context.CartoContext()
    #     with self.assertRaises(TypeError):
    #         credentials.set_credentials(base_url=self.base_url[::-1],
    #                                     api_key=self.key[::-1], overwrite=False)
    #     credentials.set_credentials(base_url=self.base_url[::-1],
    #                                 api_key=self.key[::-1], overwrite=True)
    #     self.assertEqual(credentials.credentials(),
    #                      dict(api_key=self.key[::-1],
    #                           base_url=self.base_url[::-1]))

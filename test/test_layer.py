"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, Layer, QueryLayer

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

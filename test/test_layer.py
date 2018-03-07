"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, QueryLayer, AbstractLayer, Layer
from cartoframes import styling
import pandas as pd


class TestAbstractLayer(unittest.TestCase):
    def test_class(self):
        self.assertIsNone(AbstractLayer().__init__())


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.coffee_temps = pd.DataFrame({
            'a': range(4),
            'b': list('abcd')
        })

    def test_layer_setup_dataframe(self):
        """layer.Layer._setup()"""
        layer = Layer('cortado', source=self.coffee_temps)

        with self.assertRaises(NotImplementedError):
            layer._setup([BaseMap(), layer], 1)


class TestBaseMap(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        # basemaps with baked-in labels
        self.dark_map_all = BaseMap(source='dark')
        self.light_map_all = BaseMap(source='light')
        self.voyager_labels_under = BaseMap(source='voyager')

        # basemaps with no labels
        self.dark_map_no_labels = BaseMap(source='dark',
                                          labels=None)
        self.light_map_no_labels = BaseMap(source='light',
                                           labels=None)
        self.voyager_map_no_labels = BaseMap(source='voyager',
                                             labels=None)

        # labels with no basemaps
        self.dark_only_labels = BaseMap(source='dark',
                                        only_labels=True)
        self.light_only_labels = BaseMap(source='light',
                                         only_labels=True)
        self.voyager_only_labels = BaseMap(source='voyager',
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
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'dark_all/{z}/{x}/{y}.png')
        self.assertEqual(self.light_map_all.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'light_all/{z}/{x}/{y}.png')
        self.assertEqual(self.voyager_labels_under.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'voyager_labels_under/{z}/{x}/{y}.png')
        self.assertEqual(self.dark_map_no_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'dark_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(self.light_map_no_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'light_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(self.voyager_map_no_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'voyager_nolabels/{z}/{x}/{y}.png')
        self.assertEqual(self.light_only_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'light_only_labels/{z}/{x}/{y}.png')
        self.assertEqual(self.dark_only_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'dark_only_labels/{z}/{x}/{y}.png')
        self.assertEqual(self.voyager_only_labels.url,
                         'https://{s}.basemaps.cartocdn.com/rastertiles/'
                         'voyager_only_labels/{z}/{x}/{y}.png')

        # ensure self.is_basic() works as intended
        self.assertTrue(self.light_map_all.is_basic(),
                        msg='is a basic carto basemap')
        self.assertTrue(self.dark_map_all.is_basic())
        self.assertTrue(self.voyager_labels_under.is_basic(),
                        msg='is a basic carto basemap')


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
        str_colors = ('#FF0000', 'aliceblue', 'cookie_monster', 'big_bird')
        str_colors_ans = ('#FF0000', 'aliceblue', 'cookie_monster', 'big_bird')
        str_scheme_ans = (None, None, styling.mint(5), styling.antique(10))

        for idx, color in enumerate(str_colors):
            qlayer = QueryLayer(self.query, color=color)
            qlayer.geom_type = 'point'
            if color == 'cookie_monster':
                qlayer.style_cols[color] = 'number'
                qlayer._setup([BaseMap(), qlayer], 1)
            elif color == 'big_bird':
                qlayer.style_cols[color] = 'string'
                qlayer._setup([BaseMap(), qlayer], 1)
            self.assertEqual(qlayer.color, str_colors_ans[idx])
            self.assertEqual(qlayer.scheme, str_scheme_ans[idx])

        with self.assertRaises(ValueError,
                               msg='styling value cannot be a date'):
            qlayer = QueryLayer(self.query, color='datetime_column')
            qlayer.style_cols['datetime_column'] = 'date'
            qlayer._setup([BaseMap(), qlayer], 1)

        # Exception testing
        # color column cannot be a geometry column
        with self.assertRaises(ValueError,
                               msg='color clumn cannot be a geometry column'):
            QueryLayer(self.query, color='the_geom')

        # color dict must have a 'column' key
        with self.assertRaises(ValueError,
                               msg='color dict must have a `column` key'):
            QueryLayer(self.query, color={'scheme': styling.vivid(10)})

    def test_querylayer_time_category(self):
        """layer.QueryLayer time with categories"""
        ql = QueryLayer(self.query,
                        time='timecol',
                        color='colorcol')
        # category type
        ql.style_cols['colorcol'] = 'string'
        ql.style_cols['timecol'] = 'date'

        # if non-point geoms are present (or None), raise an error
        with self.assertRaises(
                ValueError,
                msg='cannot make torque map with non-point geometries'):
            ql._setup([BaseMap(), ql], 1)

        ql.geom_type = 'point'
        # normal behavior for point geometries
        ql._setup([BaseMap(), ql], 1)
        self.assertDictEqual(ql.scheme,
                             dict(name='Antique', bin_method='',
                                  bins=[str(i) for i in range(1, 11)]))
        # expect category maps query
        with open('qlayerquery.txt', 'w') as f:
            f.write(ql.query)
        self.assertRegexpMatches(ql.query,
                                 '(?s)^SELECT\norig\.\*,\s__wrap\.'
                                 'cf_value_colorcol\n.*GROUP\sBY.*orig\.'
                                 'colorcol$')
        # cartocss should have cdb math mode
        self.assertRegexpMatches(ql.cartocss,
                                 '.*CDB_Math_Mode\(cf_value_colorcol\).*')

    def test_querylayer_time_numeric(self):
        """layer.QueryLayer time with quantitative classification"""
        ql = QueryLayer(self.query,
                        time='timecol',
                        color='colorcol')
        # category type
        ql.style_cols['colorcol'] = 'number'
        ql.style_cols['timecol'] = 'date'
        ql.geom_type = 'point'

        # normal behavior for point geometries
        ql._setup([BaseMap(), ql], 1)
        self.assertDictEqual(ql.scheme,
                             styling.mint(5))
        # expect category maps query
        self.assertRegexpMatches(ql.query.strip(),
                                 '^SELECT \*, colorcol as value '
                                 '.*_wrap$')
        # cartocss should have cdb math mode
        self.assertRegexpMatches(ql.cartocss,
                                 '.*avg\(colorcol\).*')

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

        with self.assertRaises(ValueError):
            ql = QueryLayer('select * from watermelon', time='seeds')
            ql.style_cols['seeds'] = 'string'
            ql.geom_type = 'point'
            ql._setup([BaseMap(), ql], 1)

        with self.assertRaises(ValueError):
            ql = QueryLayer('select * from watermelon', time='seeds')
            ql.style_cols['seeds'] = 'date'
            ql.geom_type = 'polygon'
            ql._setup([BaseMap(), ql], 1)

    def test_querylayer_time_default(self):
        """layer.QueryLayer time defaults"""
        time_ans = {'column': 'time_col',
                    'method': 'count',
                    'cumulative': False,
                    'frames': 256,
                    'duration': 30,
                    'trails': 2}
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
                    'cumulative': False,
                    'trails': 2}

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
        size_col_ans = {
            'column': 'cold_brew',
            'range': [5, 25],
            'bins': 5,
            'bin_method': 'quantiles'
        }
        self.assertDictEqual(qlayer.size, size_col_ans,
                             msg='size column should receive defaults')

        qlayer = QueryLayer(self.query,
                            size={
                                'column': 'cold_brew',
                                'range': [4, 15],
                                'bin_method': 'equal'
                            })
        ans = {
            'column': 'cold_brew',
            'range': [4, 15],
            'bins': 5,
            'bin_method': 'equal'
        }
        self.assertDictEqual(qlayer.size, ans,
                             msg=('size dict should receive defaults if not '
                                  'provided'))
        qlayer = QueryLayer(self.query, size={
                                            'column': 'cold_brew',
                                            'min': 10,
                                            'max': 20
                                        })
        ans = {
            'column': 'cold_brew',
            'range': [10, 20],
            'bins': 5,
            'bin_method': 'quantiles'
        }
        self.assertDictEqual(qlayer.size, ans)

    def test_querylayer_get_cartocss(self):
        """layer.QueryLayer._get_cartocss"""
        qlayer = QueryLayer(self.query, size=dict(column='cold_brew', min=10,
                                                  max=20))
        qlayer.geom_type = 'point'
        self.assertRegexpMatches(
            qlayer._get_cartocss(BaseMap()),
            ('.*marker-width:\sramp\(\[cold_brew\],\srange\(10,20\),\s'
             'quantiles\(5\)\).*')
        )

        # test line cartocss
        qlayer = QueryLayer(self.query)
        qlayer.geom_type = 'line'
        self.assertRegexpMatches(qlayer._get_cartocss(BaseMap()),
                                 '^\#layer.*line\-width.*$')
        # test point, line, polygon
        for g in ('point', 'line', 'polygon', ):
            styles = {'point': 'marker\-fill',
                      'line': 'line\-color',
                      'polygon': 'polygon\-fill'}
            qlayer = QueryLayer(self.query, color='colname')
            qlayer.geom_type = g
            self.assertRegexpMatches(qlayer._get_cartocss(BaseMap()),
                                     '^\#layer.*{}.*\}}$'.format(styles[g]))

        # geometry type should be defined
        with self.assertRaises(ValueError,
                               msg='invalid geometry type'):
            ql = QueryLayer(self.query, color='red')
            ql.geom_type = 'notvalid'
            ql._get_cartocss(BaseMap())

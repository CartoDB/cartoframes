"""Unit tests for cartoframes.layers"""
import unittest
import pandas as pd
from cartoframes.layer import BaseMap, QueryLayer, AbstractLayer, Layer
from cartoframes import styling, BinMethod


class TestAbstractLayer(unittest.TestCase):
    """Test AbstractLayer class"""
    def test_class(self):
        """basic test"""
        self.assertIsNone(AbstractLayer().__init__())


class TestLayer(unittest.TestCase):
    """Test Layer class"""
    def setUp(self):
        self.coffee_temps = pd.DataFrame({
            'a': range(4),
            'b': list('abcd')
        })

    def test_layer_setup_dataframe(self):
        """layer.Layer._setup()"""
        layer = Layer('cortado', source=self.coffee_temps)

        with self.assertRaises(NotImplementedError):
            layer._setup([BaseMap(), layer], 1)  # pylint: disable=protected-access


class TestBaseMap(unittest.TestCase):  # pylint: disable=too-many-instance-attributes
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

    def test_basemap_repr(self):
        """layer.Basemap.__repr__"""
        self.assertEqual(
            self.dark_only_labels.__repr__(),
            'BaseMap(source=dark, labels=back, only_labels=True)'
        )

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
                qlayer._setup([BaseMap(), qlayer], 1)  # pylint: disable=protected-access
            elif color == 'big_bird':
                qlayer.style_cols[color] = 'string'
                qlayer._setup([BaseMap(), qlayer], 1)  # pylint: disable=protected-access
            self.assertEqual(qlayer.color, str_colors_ans[idx])
            self.assertEqual(qlayer.scheme, str_scheme_ans[idx])

        with self.assertRaises(ValueError,
                               msg='styling value cannot be a date'):
            qlayer = QueryLayer(self.query, color='datetime_column')
            qlayer.style_cols['datetime_column'] = 'date'
            qlayer._setup([BaseMap(), qlayer], 1)  # pylint: disable=protected-access

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
        querylayer = QueryLayer(self.query,
                                time='timecol',
                                color='colorcol')
        # category type
        querylayer.style_cols['colorcol'] = 'string'
        querylayer.style_cols['timecol'] = 'date'

        # if non-point geoms are present (or None), raise an error
        with self.assertRaises(
                ValueError,
                msg='cannot make torque map with non-point geometries'):
            querylayer._setup([BaseMap(), querylayer], 1)  # pylint: disable=protected-access

        querylayer.geom_type = 'point'
        # normal behavior for point geometries
        querylayer._setup([BaseMap(), querylayer], 1)  # pylint: disable=protected-access
        self.assertDictEqual(querylayer.scheme,
                             dict(name='Antique', bin_method='',
                                  bins=[str(i) for i in range(1, 11)]))
        # expect category maps query
        self.assertRegexpMatches(querylayer.query,
                                 r'(?s)^SELECT\norig\.\*,\s__wrap\.'
                                 r'cf_value_colorcol\n.*GROUP\sBY.*orig\.'
                                 r'colorcol$')
        # cartocss should have cdb math mode
        self.assertRegexpMatches(querylayer.cartocss,
                                 r'.*CDB_Math_Mode\(cf_value_colorcol\).*')

    def test_querylayer_time_numeric(self):
        """layer.QueryLayer time with quantitative classification"""
        querylayer = QueryLayer(self.query,
                                time='timecol',
                                color='colorcol')
        # category type
        querylayer.style_cols['colorcol'] = 'number'
        querylayer.style_cols['timecol'] = 'date'
        querylayer.geom_type = 'point'

        # normal behavior for point geometries
        querylayer._setup([BaseMap(), querylayer], 1)  # pylint: disable=protected-access
        self.assertDictEqual(querylayer.scheme,
                             styling.mint(5))
        # expect category maps query
        self.assertRegexpMatches(querylayer.query.strip(),
                                 r'^SELECT \*, colorcol as value '
                                 r'.*_wrap$')
        # cartocss should have cdb math mode
        self.assertRegexpMatches(querylayer.cartocss,
                                 r'.*avg\(colorcol\).*')

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
            querylayer = QueryLayer('select * from watermelon', time='seeds')
            querylayer.style_cols['seeds'] = 'string'
            querylayer.geom_type = 'point'
            querylayer._setup([BaseMap(), querylayer], 1)  # pylint: disable=protected-access

        with self.assertRaises(ValueError):
            querylayer = QueryLayer('select * from watermelon', time='seeds')
            querylayer.style_cols['seeds'] = 'date'
            querylayer.geom_type = 'polygon'
            querylayer._setup([BaseMap(), querylayer], 1)  # pylint: disable=protected-access

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
        qlayer.geom_type = 'point'
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
        qlayer = QueryLayer(
            self.query,
            size={
                'column': 'cold_brew',
                'min': 10,
                'max': 20
            }
        )
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
            qlayer._get_cartocss(BaseMap()),  # pylint: disable=protected-access
            (r'.*marker-width:\sramp\(\[cold_brew\],\srange\(10,20\),\s'
             r'quantiles\(5\)\).*')
        )

        # test line cartocss
        qlayer = QueryLayer(self.query)
        qlayer.geom_type = 'line'
        self.assertRegexpMatches(
            qlayer._get_cartocss(BaseMap()),  # pylint: disable=protected-access
            r'^\#layer.*line\-width.*$'
        )
        # test point, line, polygon
        for geom in ('point', 'line', 'polygon', ):
            styles = {'point': r'marker\-fill',
                      'line': r'line\-color',
                      'polygon': r'polygon\-fill'}
            qlayer = QueryLayer(self.query, color='colname')
            qlayer.geom_type = geom
            self.assertRegexpMatches(
                qlayer._get_cartocss(BaseMap()),  # pylint: disable=protected-access
                r'^\#layer.*{}.*\}}$'.format(styles[geom])
            )

        # geometry type should be defined
        with self.assertRaises(ValueError,
                               msg='invalid geometry type'):
            querylayer = QueryLayer(self.query, color='red')
            querylayer.geom_type = 'notvalid'
            querylayer._get_cartocss(BaseMap())  # pylint: disable=protected-access

    def test_line_styling(self):  # pylint: disable=too-many-statements
        """layer.QueryLayer line styling"""
        linelayer = QueryLayer(
            'select * from lines',
            size=5
        )

        linelayer.geom_type = 'line'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: 5' in linelayer.cartocss
        )


        size = 'size_col'
        color = 'mag'
        linelayer = QueryLayer('select * from lines', size=size, color=color)

        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: ramp([size_col], range(1,5), quantiles(5))' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Mint), quantiles(5), >)' in linelayer.cartocss
        )


        size = {'column': 'size_col'}
        color = 'mag'
        linelayer = QueryLayer('select * from lines', size=size, color=color)

        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: ramp([size_col], range(1,5), quantiles(5))' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Mint), quantiles(5), >)' in linelayer.cartocss
        )


        size = {
            'column': 'size_col',
            'range': (5, 10)
        }
        color = 'mag'
        linelayer = QueryLayer('select * from lines', size=size, color=color)
        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: ramp([size_col], range(5,10), quantiles(5))' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Mint), quantiles(5), >)' in linelayer.cartocss
        )


        size = 1.5
        color = 'mag'

        linelayer = QueryLayer('select * from lines', size=size, color=color)

        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: 1.5' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Mint), quantiles(5), >)' in linelayer.cartocss
        )


        size = {
            'column': 'size_col',
            'range': [2, 6]
        }

        color = {
            'column': 'mag',
            'scheme': styling.sunset(7)
        }

        linelayer = QueryLayer('select * from lines', size=size, color=color)

        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: ramp([size_col], range(2,6), quantiles(5))' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Sunset), quantiles(7), >)' in linelayer.cartocss
        )


        # size and color
        size = {
            'column': 'size_col',
            'range': [2, 6],
            'bin_method': BinMethod.jenks
        }
        color = {
            'column': 'mag',
            'scheme': styling.sunset(7)
        }

        linelayer = QueryLayer(
            'select * from lines',
            size=size,
            color=color
        )

        linelayer.geom_type = 'line'
        linelayer.style_cols['mag'] = 'number'
        linelayer.style_cols['size_col'] = 'number'
        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-width: ramp([size_col], range(2,6), jenks(5))' in linelayer.cartocss
        )

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Sunset), quantiles(7), >)' in linelayer.cartocss
        )

        # category lines

        linelayer = QueryLayer(
            'select * from lines',
            color={'column': 'mag', 'scheme': styling.antique(7)}
        )

        linelayer.geom_type = 'line'

        linelayer._setup([BaseMap(), linelayer], 1)  # pylint: disable=protected-access

        self.assertTrue(
            'line-color: ramp([mag], cartocolor(Antique), category(7), =)'
            in linelayer.cartocss
        )

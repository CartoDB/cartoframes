import unittest

from cartoframes.viz import Legend


class TestLegend(unittest.TestCase):
    def test_is_legend_defined(self):
        """Legend"""
        self.assertNotEqual(Legend, None)

    def test_legend_init(self):
        """Legend should be properly initialized"""
        legend = Legend({
            'type': 'color-category',
            'prop': 'strokeColor',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        self.assertEqual(legend._type, 'color-category')
        self.assertEqual(legend._prop, 'strokeColor')
        self.assertEqual(legend._title, '[TITLE]')
        self.assertEqual(legend._description, '[description]')
        self.assertEqual(legend._footer, '[footer]')

    def test_legend_info(self):
        """Legend should return a proper information object"""
        legend = Legend({
            'type': 'color-category',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        self.assertEqual(legend.get_info(), {
            'type': 'color-category',
            'prop': 'color',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        legend = Legend({
            'type': {
                'point': 'color-category-point',
                'line': 'color-category-line',
                'polygon': 'color-category-polygon'
            }
        })

        self.assertEqual(legend.get_info('line'), {
            'type': 'color-category-line',
            'prop': 'color',
            'title': '',
            'description': '',
            'footer': ''
        })

    def test_wrong_input(self):
        """Legend should raise an error if legend input is not valid"""
        msg = 'Wrong legend input.'
        with self.assertRaisesRegexp(ValueError, msg):
            Legend(1234)

    def test_wrong_type(self):
        """Legend should raise an error if legend type is not valid"""
        msg = 'Legend type is not valid. Valid legend types are: color-bins, '
        'color-bins-line, color-bins-point, color-bins-polygon, color-category, '
        'color-category-line, color-category-point, color-category-polygon, '
        'color-continuous, color-continuous-line, color-continuous-point, '
        'color-continuous-polygon, size-bins, size-bins-point, size-continuous, '
        'size-continuous-point.'
        with self.assertRaisesRegexp(ValueError, msg):
            Legend({'type': 'xxx'}).get_info()

    def test_wrong_prop(self):
        """Legend should raise an error if legend prop is not valid"""
        msg = 'Legend property is not valid. Valid legend properties are: '
        'color, strokeColor, width, strokeWidth.'
        with self.assertRaisesRegexp(ValueError, msg):
            Legend({'type': 'color-category', 'prop': 'xxx'}).get_info()

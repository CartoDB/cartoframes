import unittest

from cartoframes.viz import Widget


class TestWidget(unittest.TestCase):
    def test_is_widget_defined(self):
        """Widget"""
        self.assertNotEqual(Widget, None)

    def test_widget_init(self):
        """Widget should be properly initialized"""
        widget = Widget({
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        self.assertEqual(widget._type, 'formula')
        self.assertEqual(widget._title, '[TITLE]')
        self.assertEqual(widget._description, '[description]')
        self.assertEqual(widget._footer, '[footer]')

    def test_widget_info(self):
        """Widget should return a proper information object"""
        widget = Widget({
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        self.assertEqual(widget.get_info(), {
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]',
            'has_bridge': False,
            'prop': '',
            'variable_name': 'vb6dbcf',
            'options': {'readOnly': False}
        })

    def test_wrong_input(self):
        """Widget should raise an error if the input is not valid"""
        msg = 'Wrong widget input.'
        with self.assertRaisesRegexp(ValueError, msg):
            Widget(1234)

    def test_wrong_type(self):
        """Widget should raise an error if widget type is not valid"""
        msg = 'Widget type is not valid. Valid widget types are: default, formula.'

        with self.assertRaisesRegexp(ValueError, msg):
            Widget({'type': 'xxx'}).get_info()

    def test_animation_widget(self):
        """An Animation widget should be created successfully with the default property"""
        widget = Widget({
            'type': 'animation',
        })

        self.assertEqual(widget.get_info(), {
            'type': 'animation',
            'title': '',
            'value': '',
            'description': '',
            'footer': '',
            'has_bridge': True,
            'prop': 'filter',
            'variable_name': '',
            'options': {'readOnly': False}
        })

    def test_animation_widget_prop(self):
        """An Animation widget should be created successfully with a custom property"""
        widget = Widget({
            'type': 'animation',
            'prop': 'width'
        })

        self.assertEqual(widget.get_info(), {
            'type': 'animation',
            'title': '',
            'value': '',
            'description': '',
            'footer': '',
            'has_bridge': True,
            'prop': 'width',
            'variable_name': '',
            'options': {'readOnly': False}
        })

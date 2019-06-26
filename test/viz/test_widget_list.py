import unittest

from cartoframes.viz import WidgetList
from cartoframes.viz import Widget

widget_a = {
    'type': 'formula',
    'value': 'viewportSum($amount)',
    'title': '[TITLE]',
    'description': '[description]',
    'footer': '[footer]'
}

widget_b = {
    'type': 'default',
    'value': '"Custom Info"',
}


class TestWidgetList(unittest.TestCase):
    def test_is_widget_list_defined(self):
        """WidgetList"""
        self.assertNotEqual(WidgetList, None)

    def test_widget_list_init_with_a_dict(self):
        """WidgetList should be properly initialized"""
        widget_list = WidgetList(widget_a)

        self.assertEqual(widget_list.widgets[0]._type, 'formula')
        self.assertEqual(widget_list.widgets[0]._value, 'viewportSum($amount)')
        self.assertEqual(widget_list.widgets[0]._title, '[TITLE]')
        self.assertEqual(widget_list.widgets[0]._description, '[description]')
        self.assertEqual(widget_list.widgets[0]._footer, '[footer]')
        self.assertNotEqual(widget_list.widgets[0]._name, None)
        self.assertTrue(isinstance(widget_list.widgets[0], Widget))

    def test_widget_list_init_with_a_list_of_dict(self):
        """WidgetList should be properly initialized"""

        widget_list = WidgetList([widget_a, widget_b])

        self.assertEqual(widget_list.widgets[0]._type, 'formula')
        self.assertEqual(widget_list.widgets[0]._value, 'viewportSum($amount)')
        self.assertEqual(widget_list.widgets[0]._title, '[TITLE]')
        self.assertEqual(widget_list.widgets[0]._description, '[description]')
        self.assertEqual(widget_list.widgets[0]._footer, '[footer]')
        self.assertNotEqual(widget_list.widgets[0]._name, None)
        self.assertTrue(isinstance(widget_list.widgets[0], Widget))

        self.assertEqual(widget_list.widgets[1]._type, 'default')
        self.assertEqual(widget_list.widgets[1]._value, '"Custom Info"')
        self.assertEqual(widget_list.widgets[1]._title, '')
        self.assertEqual(widget_list.widgets[1]._description, '')
        self.assertEqual(widget_list.widgets[1]._footer, '')
        self.assertNotEqual(widget_list.widgets[1]._name, None)
        self.assertTrue(isinstance(widget_list.widgets[1], Widget))

    def test_widget_list_init_with_a_widget(self):
        """WidgetList should be properly initialized"""
        widget_list = WidgetList(Widget(widget_a))
        self.assertTrue(isinstance(widget_list.widgets[0], Widget))

    def test_widget_list_init_with_a_list_of_widgets(self):
        """WidgetList should be properly initialized"""

        widget_list = WidgetList([
          Widget(widget_a),
          Widget(widget_b)
        ])

        self.assertTrue(isinstance(widget_list.widgets[0], Widget))
        self.assertTrue(isinstance(widget_list.widgets[1], Widget))

    def test_widget_list_variables(self):
        """Widget List should return a proper variables object"""
        widget_list = WidgetList([
          Widget(widget_a),
          Widget(widget_b)
        ])

        variables = widget_list.get_variables()
        self.assertEqual(variables, {
            'vb6dbcf': 'viewportSum($amount)'
        })

    def test_widget_list_variables_when_is_empty(self):
        """Widget List should return an empty dict"""

        widget_list = WidgetList()
        variables = widget_list.get_variables()
        self.assertEqual(variables, {})

import unittest
from cartoframes.viz import widgets


class TestDefaultWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.default_widget, None)

    def test_factory(self):
        "should create a default widget"
        widget = widgets.default_widget(title='Default Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'default')
        self.assertEqual(widget_info.get('title'), 'Default Widget')

import unittest
from cartoframes.viz import widgets


class TestHistogramWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.histogram_widget, None)

    def test_factory(self):
        "should create a histogram widget"
        widget = widgets.histogram_widget('$value', title='Histogram Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'histogram')
        self.assertEqual(widget_info.get('value'), '$value')
        self.assertEqual(widget_info.get('title'), 'Histogram Widget')
        self.assertEqual(widget_info.get('options').get('readOnly'), False)

import unittest
from cartoframes.viz import widgets


class TestTimeSeriesWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.time_series_widget, None)

    def test_factory(self):
        "should create a time series widget"
        widget = widgets.time_series_widget('$value', title='Time Series Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'time-series')
        self.assertEqual(widget_info.get('value'), '$value')
        self.assertEqual(widget_info.get('title'), 'Time Series Widget')
        self.assertEqual(widget_info.get('read_only'), False)

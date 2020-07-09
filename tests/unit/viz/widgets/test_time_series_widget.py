from cartoframes.viz import widgets


class TestTimeSeriesWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.time_series_widget is not None

    def test_factory(self):
        "should create a time series widget"
        widget = widgets.time_series_widget("prop('value')", title='Time Series Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'time-series'
        assert widget_info.get('value') == "prop('value')"
        assert widget_info.get('title') == 'Time Series Widget'
        assert widget_info.get('options').get('readOnly') is False

from cartoframes.viz import widgets


class TestHistogramWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.histogram_widget is not None

    def test_factory(self):
        "should create a histogram widget"
        widget = widgets.histogram_widget("prop('value')", title='Histogram Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'histogram'
        assert widget_info.get('value') == "prop('value')"
        assert widget_info.get('title') == 'Histogram Widget'
        assert widget_info.get('options').get('readOnly') is False

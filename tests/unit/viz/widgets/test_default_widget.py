from cartoframes.viz import widgets


class TestDefaultWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.default_widget is not None

    def test_factory(self):
        "should create a default widget"
        widget = widgets.default_widget(title='Default Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'default'
        assert widget_info.get('title') == 'Default Widget'

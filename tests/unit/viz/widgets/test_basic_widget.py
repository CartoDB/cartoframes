from cartoframes.viz import widgets


class TestBasicWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.basic_widget is not None

    def test_factory(self):
        "should create a basic widget"
        widget = widgets.basic_widget(title='Default Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'basic'
        assert widget_info.get('title') == 'Default Widget'

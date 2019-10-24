from cartoframes.viz import widgets


class TestAnimationWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.animation_widget is not None

    def test_factory(self):
        "should create an animation widget"
        widget = widgets.animation_widget(title='Animation Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'animation'
        assert widget_info.get('title') == 'Animation Widget'

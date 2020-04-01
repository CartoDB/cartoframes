from cartoframes.viz import widgets


class TestCategoryWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.category_widget is not None

    def test_factory(self):
        "should create a category widget"
        widget = widgets.category_widget("prop('value')", title='Category Widget')
        widget_info = widget.get_info()
        assert widget_info.get('type') == 'category'
        assert widget_info.get('value') == "prop('value')"
        assert widget_info.get('title') == 'Category Widget'
        assert widget_info.get('options').get('readOnly') is False

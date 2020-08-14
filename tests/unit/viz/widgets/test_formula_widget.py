from cartoframes.viz import widgets


class TestFormulaWidget(object):
    def test_widgets(self):
        "should be defined"
        assert widgets.formula_widget is not None

    def test_factory(self):
        "should create a default formula widget"
        widget = widgets.formula_widget('value', title='Formula Widget')
        widget_info = widget.get_info()

        assert widget_info.get('type') == 'formula'
        assert widget_info.get('value') == 'value'
        assert widget_info.get('title') == 'Formula Widget'

    def test_count_formula_viewport(self):
        "should create a formula widget to count viewport features"
        widget = widgets.formula_widget('count')
        widget_info = widget.get_info()
        assert widget_info.get('value') == 'count'
        assert widget_info.get('is_global') == False  # noqa

    def test_count_formula_global(self):
        "should create a formula widget to count global features"
        widget = widgets.formula_widget('count', is_global=True)
        widget_info = widget.get_info()
        assert widget_info.get('value') == 'count'
        assert widget_info.get('is_global') == True  # noqa

    def test_formula_viewport(self):
        "should create a formula widget to get a viewport operation"
        widget = widgets.formula_widget('value', operation='avg')
        widget_info = widget.get_info()
        assert widget_info.get('value') == 'value'
        assert widget_info.get('operation') == 'avg'
        assert widget_info.get('is_global') == False  # noqa

    def test_formula_global(self):
        "should create a formula widget to get a global operation"
        widget = widgets.formula_widget('value', operation='avg', is_global=True)
        widget_info = widget.get_info()
        assert widget_info.get('value') == 'value'
        assert widget_info.get('operation') == 'avg'
        assert widget_info.get('is_global') == True  # noqa

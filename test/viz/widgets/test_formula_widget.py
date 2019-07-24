import unittest
from cartoframes.viz import widgets


class TestFormulaWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.formula_widget, None)

    def test_factory(self):
        "should create a default formula widget"
        widget = widgets.formula_widget('value', title='Formula Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'formula')
        self.assertEqual(widget_info.get('value'), '$value')
        self.assertEqual(widget_info.get('title'), 'Formula Widget')

    def test_count_formula_viewport(self):
        "should create a formula widget to count viewport features"
        widget = widgets.formula_widget('count')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('value'), 'viewportCount()')

    def test_count_formula_global(self):
        "should create a formula widget to count global features"
        widget = widgets.formula_widget('count', is_global=True)
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('value'), 'globalCount()')

    def test_formula_viewport(self):
        "should create a formula widget to get a viewport operation"
        widget = widgets.formula_widget('value', 'avg')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('value'), 'viewportAvg($value)')

    def test_formula_global(self):
        "should create a formula widget to get a global operation"
        widget = widgets.formula_widget('value', 'avg', is_global=True)
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('value'), 'globalAvg($value)')

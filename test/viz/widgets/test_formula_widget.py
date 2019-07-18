import unittest
from cartoframes.viz import widgets


class TestFormulaWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.formula_widget, None)

    def test_factory(self):
        "should create a formula widget"
        widget = widgets.formula_widget('$value', title='Formula Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'formula')
        self.assertEqual(widget_info.get('value'), '$value')
        self.assertEqual(widget_info.get('title'), 'Formula Widget')

import unittest
from cartoframes.viz import widgets


class TestCategoryWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.category_widget, None)

    def test_factory(self):
        "should create a category widget"
        widget = widgets.category_widget('$value', title='Category Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'category')
        self.assertEqual(widget_info.get('value'), '$value')
        self.assertEqual(widget_info.get('title'), 'Category Widget')
        self.assertEqual(widget_info.get('read_only'), False)

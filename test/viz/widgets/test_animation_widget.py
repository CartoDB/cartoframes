import unittest
from cartoframes.viz import widgets


class TestAnimationWidget(unittest.TestCase):
    def test_widgets(self):
        "should be defined"
        self.assertNotEqual(widgets.animation_widget, None)

    def test_factory(self):
        "should create an animation widget"
        widget = widgets.animation_widget(title='Animation Widget')
        widget_info = widget.get_info()
        self.assertEqual(widget_info.get('type'), 'animation')
        self.assertEqual(widget_info.get('title'), 'Animation Widget')

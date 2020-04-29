from cartoframes.viz.widget import Widget
from cartoframes.viz.widget_list import WidgetList
from cartoframes.viz import formula_widget, basic_widget

WIDGET_A = formula_widget(
    'amount',
    operation='sum',
    title='[TITLE]',
    description='[description]',
    footer='[footer]'
)

WIDGET_B = basic_widget(title='Custom Info')


class TestWidgetList(object):
    def test_is_widget_list_defined(self):
        """WidgetList"""
        assert WidgetList is not None

    def test_widget_list_init_with_a_dict(self):
        """WidgetList should be properly initialized"""
        widget_list = WidgetList([WIDGET_A])

        assert widget_list._widgets[0]._type == 'formula'
        assert widget_list._widgets[0]._value == "viewportSum(prop('amount'))"
        assert widget_list._widgets[0]._title == '[TITLE]'
        assert widget_list._widgets[0]._description == '[description]'
        assert widget_list._widgets[0]._footer == '[footer]'
        assert isinstance(widget_list._widgets[0], Widget)

    def test_widget_list_init_with_a_list_of_dict(self):
        """WidgetList should be properly initialized"""

        widget_list = WidgetList([WIDGET_A, WIDGET_B])

        assert widget_list._widgets[0]._type == 'formula'
        assert widget_list._widgets[0]._value == "viewportSum(prop('amount'))"
        assert widget_list._widgets[0]._title == '[TITLE]'
        assert widget_list._widgets[0]._description == '[description]'
        assert widget_list._widgets[0]._footer == '[footer]'
        assert isinstance(widget_list._widgets[0], Widget)

        assert widget_list._widgets[1]._type == 'basic'
        assert widget_list._widgets[1]._title == 'Custom Info'
        assert widget_list._widgets[1]._description is None
        assert widget_list._widgets[1]._footer is None
        assert isinstance(widget_list._widgets[1], Widget)

    def test_widget_list_init_with_a_widget(self):
        """WidgetList should be properly initialized"""
        widget_list = WidgetList([WIDGET_A])
        assert isinstance(widget_list._widgets[0], Widget)

    def test_widget_list_init_with_a_list_of_widgets(self):
        """WidgetList should be properly initialized"""

        widget_list = WidgetList([WIDGET_A, WIDGET_B])

        assert isinstance(widget_list._widgets[0], Widget)
        assert isinstance(widget_list._widgets[1], Widget)

    def test_widget_list_get_widgets_info(self):
        """Widget List should return a proper widgets info object"""

        widget_list = WidgetList([WIDGET_A, WIDGET_B])
        widgets_info = widget_list.get_widgets_info()
        assert widgets_info == [
            {
                'type': 'formula',
                'value': "viewportSum(prop('amount'))",
                'title': '[TITLE]',
                'prop': '',
                'description': '[description]',
                'footer': '[footer]',
                'has_bridge': False,
                'variable_name': 'vdb8cc1',
                'options': {
                    'readOnly': False,
                    'buckets': 20,
                    'weight': 1,
                    'autoplay': True,
                    'format': None
                }
            }, {
                'type': 'basic',
                'title': 'Custom Info',
                'value': '',
                'prop': '',
                'description': '',
                'footer': '',
                'has_bridge': False,
                'variable_name': '',
                'options': {
                    'readOnly': False,
                    'buckets': 20,
                    'weight': 1,
                    'autoplay': True,
                    'format': None
                }
            }]

import pytest

from cartoframes.viz.widget import Widget


class TestWidget(object):
    def test_is_widget_defined(self):
        """Widget"""
        assert Widget is not None

    def test_widget_init(self):
        """Widget should be properly initialized"""
        widget = Widget('formula', 'amount', '[title]', '[description]', '[footer]')

        assert widget._type == 'formula'
        assert widget._title == '[title]'
        assert widget._description == '[description]'
        assert widget._footer == '[footer]'

    def test_widget_info(self):
        """Widget should return a proper information object"""
        widget = Widget('formula', 'amount', '[title]', '[description]', '[footer]')

        assert widget.get_info() == {
            'type': 'formula',
            'value': 'amount',
            'title': '[title]',
            'description': '[description]',
            'footer': '[footer]',
            'has_bridge': False,
            'prop': '',
            'variable_name': 'v9cb6ff',
            'options': {
                'readOnly': False,
                'buckets': 20,
                'weight': 1,
                'autoplay': True
            }
        }

    def test_wrong_type(self):
        """Widget should raise an error if widget type is not valid"""
        msg = 'Widget type is not valid. Valid widget types are: ' + \
            'basic, default, formula, histogram, category, animation, time-series.'

        with pytest.raises(ValueError) as e:
            Widget({'type': 'xxx'}).get_info()
        assert str(e.value) == msg

    def test_animation_widget(self):
        """An Animation widget should be created successfully with the default property"""
        widget = Widget('animation', prop='filter')

        assert widget.get_info() == {
            'type': 'animation',
            'title': '',
            'value': '',
            'description': '',
            'footer': '',
            'has_bridge': True,
            'prop': 'filter',
            'variable_name': '',
            'options': {
                'readOnly': False,
                'buckets': 20,
                'weight': 1,
                'autoplay': True
            }
        }

    def test_animation_widget_prop(self):
        """An Animation widget should be created successfully with a custom property"""
        widget = Widget('animation', prop='size')

        assert widget.get_info() == {
            'type': 'animation',
            'title': '',
            'value': '',
            'description': '',
            'footer': '',
            'has_bridge': True,
            'prop': 'width',
            'variable_name': '',
            'options': {
                'readOnly': False,
                'buckets': 20,
                'weight': 1,
                'autoplay': True
            }
        }

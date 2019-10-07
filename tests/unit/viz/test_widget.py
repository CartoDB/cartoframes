import pytest

from cartoframes.viz import Widget


class TestWidget(object):
    def test_is_widget_defined(self):
        """Widget"""
        assert Widget is not None

    def test_widget_init(self):
        """Widget should be properly initialized"""
        widget = Widget({
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        assert widget._type == 'formula'
        assert widget._title == '[TITLE]'
        assert widget._description == '[description]'
        assert widget._footer == '[footer]'

    def test_widget_info(self):
        """Widget should return a proper information object"""
        widget = Widget({
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        assert widget.get_info() == {
            'type': 'formula',
            'value': 'viewportSum($amount)',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]',
            'has_bridge': False,
            'prop': '',
            'variable_name': 'vb6dbcf',
            'options': {
                'readOnly': False,
                'buckets': 20
            }
        }

    def test_wrong_input(self):
        """Widget should raise an error if the input is not valid"""
        msg = 'Wrong widget input.'
        with pytest.raises(ValueError) as e:
            Widget(1234)
        assert str(e.value) == msg

    def test_wrong_type(self):
        """Widget should raise an error if widget type is not valid"""
        msg = 'Widget type is not valid. Valid widget types are: ' + \
            'default, formula, histogram, category, animation, time-series.'

        with pytest.raises(ValueError) as e:
            Widget({'type': 'xxx'}).get_info()
        assert str(e.value) == msg

    def test_animation_widget(self):
        """An Animation widget should be created successfully with the default property"""
        widget = Widget({
            'type': 'animation',
        })

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
                'buckets': 20
            }
        }

    def test_animation_widget_prop(self):
        """An Animation widget should be created successfully with a custom property"""
        widget = Widget({
            'type': 'animation',
            'prop': 'width'
        })

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
                'buckets': 20
            }
        }

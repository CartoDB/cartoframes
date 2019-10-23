import pytest

from cartoframes.viz import Legend


class TestLegend(object):
    def test_is_legend_defined(self):
        """Legend"""
        assert Legend is not None

    def test_legend_init_dict(self):
        """Legend should be properly initialized when passing a dict"""
        legend = Legend({
            'type': 'color-category',
            'prop': 'strokeColor',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        assert legend._type == 'color-category'
        assert legend._prop == 'strokeColor'
        assert legend._title == '[TITLE]'
        assert legend._description == '[description]'
        assert legend._footer == '[footer]'
        assert legend._dynamic is True

    def test_legend_init_properties(self):
        """Legend should be properly initialized when passing properties"""
        legend = Legend('color-category',
                        prop='strokeColor',
                        title='[TITLE]',
                        description='[description]',
                        footer='[footer]',
                        dynamic=False)

        assert legend._type == 'color-category'
        assert legend._prop == 'strokeColor'
        assert legend._title == '[TITLE]'
        assert legend._description == '[description]'
        assert legend._footer == '[footer]'
        assert legend._dynamic is False

    def test_legend_info(self):
        """Legend should return a proper information object"""
        legend = Legend({
            'type': 'color-category',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

        assert legend.get_info() == {
            'type': 'color-category',
            'prop': 'color',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]',
            'dynamic': True,
            'variable': ''
        }

        legend = Legend({
            'type': {
                'point': 'color-category-point',
                'line': 'color-category-line',
                'polygon': 'color-category-polygon'
            }
        })

        assert legend.get_info('line') == {
            'type': 'color-category-line',
            'prop': 'color',
            'title': '',
            'description': '',
            'footer': '',
            'dynamic': True,
            'variable': ''
        }

    def test_wrong_input(self):
        """Legend should raise an error if legend input is not valid"""
        msg = 'Wrong legend input.'
        with pytest.raises(ValueError) as e:
            Legend(1234)
        assert str(e.value) == msg

    def test_wrong_type(self):
        """Legend should raise an error if legend type is not valid"""
        msg = 'Legend type "xxx" is not valid. Valid legend types are: default, ' +\
            'color-bins, color-bins-line, color-bins-point, color-bins-polygon, ' + \
            'color-category, color-category-line, color-category-point, color-category-polygon, ' + \
            'color-continuous, color-continuous-line, color-continuous-point, color-continuous-polygon, ' + \
            'size-bins, size-bins-line, size-bins-point, ' + \
            'size-category, size-category-line, size-category-point, ' + \
            'size-continuous, size-continuous-line, size-continuous-point.'
        with pytest.raises(ValueError) as e:
            Legend({'type': 'xxx'}).get_info()
        assert str(e.value) == msg

    def test_wrong_prop(self):
        """Legend should raise an error if legend prop is not valid"""
        msg = 'Legend property "xxx" is not valid. Valid legend properties are: ' + \
            'color, strokeColor, width, strokeWidth.'
        with pytest.raises(ValueError) as e:
            Legend({'type': 'color-category', 'prop': 'xxx'}).get_info()
        assert str(e.value) == msg

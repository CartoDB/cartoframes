import pytest

from cartoframes.viz.legend import Legend


class TestLegend(object):
    def test_is_legend_defined(self):
        """Legend"""
        assert Legend is not None

    def test_legend_init_properties(self):
        """Legend should be properly initialized when passing properties"""
        legend = Legend('color-category',
                        prop='stroke_color',
                        title='[title]',
                        description='[description]',
                        footer='[footer]',
                        dynamic=False)

        assert legend._type == 'color-category'
        assert legend._prop == 'stroke_color'
        assert legend._title == '[title]'
        assert legend._description == '[description]'
        assert legend._footer == '[footer]'
        assert legend._dynamic is False

    def test_legends_info(self):
        """Legend should return a proper information object"""
        legend = Legend('color-category',
                        title='[title]',
                        description='[description]',
                        footer='[footer]')

        assert legend.get_info() == {
            'ascending': False,
            'type': 'color-category',
            'prop': 'color',
            'title': '[title]',
            'description': '[description]',
            'footer': '[footer]',
            'dynamic': True,
            'variable': '',
            'format': None
        }

    def test_wrong_type(self):
        """Legend should raise an error if legend type is not valid"""
        msg = 'Legend type "xxx" is not valid. Valid legend types are: basic, default, ' +\
            'color-bins, color-bins-line, color-bins-point, color-bins-polygon, ' + \
            'color-category, color-category-line, color-category-point, color-category-polygon, ' + \
            'color-continuous, color-continuous-line, color-continuous-point, color-continuous-polygon, ' + \
            'size-bins, size-bins-line, size-bins-point, ' + \
            'size-category, size-category-line, size-category-point, ' + \
            'size-continuous, size-continuous-line, size-continuous-point.'
        with pytest.raises(ValueError) as e:
            Legend('xxx').get_info()
        assert str(e.value) == msg

    def test_wrong_prop(self):
        """Legend should raise an error if legend prop is not valid"""
        msg = 'Legend property "xxx" is not valid. Valid legend properties are: ' + \
            'color, stroke_color, size, stroke_width.'
        with pytest.raises(ValueError) as e:
            Legend('color-category', prop='xxx').get_info()
        assert str(e.value) == msg

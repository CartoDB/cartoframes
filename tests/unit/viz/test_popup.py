import pytest

from cartoframes.viz.popup import Popup


class TestPopup(object):
    def test_is_popup_defined(self):
        """Popup"""
        assert Popup is not None

    def test_popup_init(self):
        """Popup should be properly initialized"""
        popup_click_1 = Popup('click', 'pop')
        popup_hover_1 = Popup('hover', 'pop', 'Pop')

        assert popup_click_1.value == 'pop'
        assert popup_click_1.title == 'pop'
        assert popup_hover_1.value == 'pop'
        assert popup_hover_1.title == 'Pop'

    def test_popup_interactivity(self):
        """Popup should return a proper interactivity object"""

        popup_click_1 = Popup('click', 'pop')
        popup_hover_1 = Popup('hover', 'pop', 'Pop')

        assert popup_click_1.interactivity == {
            'event': 'click',
            'attrs': {
                'attr': 'pop',
                'title': 'pop',
                'format': None
            }
        }

        assert popup_hover_1.interactivity == {
            'event': 'hover',
            'attrs': {
                'attr': 'pop',
                'title': 'Pop',
                'format': None
            }
        }

    def test_popup_variables(self):
        """Popup should return a proper variables object"""

        popup_click_1 = Popup('click', 'pop')
        popup_hover_1 = Popup('hover', 'pop', 'Pop')

        assert popup_click_1.variable == {
            'name': 'pop',
            'value': 'pop'
        }

        assert popup_hover_1.variable == {
            'name': 'pop',
            'value': 'pop'
        }

    def test_wrong_attribute(self):
        """Popup should raise an error if popup property is not valid"""
        with pytest.raises(ValueError):
            Popup(1234)

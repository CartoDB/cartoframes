import pytest

from cartoframes.viz import Popup


class TestPopup(object):
    def test_is_popup_defined(self):
        """Popup"""
        assert Popup is not None

    def test_popup_init(self):
        """Popup should be properly initialized"""
        popup = Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'title': 'Pop',
                'value': '$pop'
            }]
        })

        assert popup._click == ['$pop', '$name']
        assert popup._hover == [{
            'title': 'Pop',
            'value': '$pop'
        }]

        popup = Popup({
            'click': '$pop',
            'hover': {
                'title': 'Pop',
                'value': '$pop'
            }
        })

        assert popup._click == ['$pop']
        assert popup._hover == [{
            'title': 'Pop',
            'value': '$pop'
        }]

    def test_popup_interactivity(self):
        """Popup should return a proper interactivity object"""
        popup = Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'title': 'Pop',
                'value': '$pop'
            }]
        })

        assert popup.get_interactivity() == [{
            'event': 'click',
            'attrs': [{
                'name': 'v559339',
                'title': '$pop'
            }, {
                'name': 'v8e0f74',
                'title': '$name'
            }]
        }, {
            'event': 'hover',
            'attrs': [{
                'name': 'v559339',
                'title': 'Pop'
            }]
        }]

    def test_popup_variables(self):
        """Popup should return a proper variables object"""
        popup = Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'title': 'Pop',
                'value': '$pop'
            }]
        })

        assert popup.get_variables() == {
            'v559339': '$pop',
            'v8e0f74': '$name'
        }

    def test_wrong_attribute(self):
        """Popup should raise an error if popup property is not valid"""
        with pytest.raises(ValueError):
            Popup(1234)

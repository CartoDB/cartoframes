from cartoframes.viz import popup_element
from cartoframes.viz.popup import Popup
from cartoframes.viz.popup_list import PopupList

popup_list = PopupList({
    'click': [popup_element('value_1'), popup_element('value_2')],
    'hover': [popup_element('value_1'), popup_element('value_3')]
})


class TestPopupList(object):
    def test_should_have_access_to_popup_elements(self):
        for element in popup_list.elements:
            assert isinstance(element, Popup)

    def test_should_get_all_popup_interactivities(self):
        assert popup_list.get_interactivity() == {
            'click': [
                {
                    'attr': 'value_2',
                    'title': 'value_2',
                    'format': None
                }, {
                    'attr': 'value_1',
                    'title': 'value_1',
                    'format': None
                }
            ],
            'hover': [
                {
                    'attr': 'value_3',
                    'title': 'value_3',
                    'format': None
                }, {
                    'attr': 'value_1',
                    'title': 'value_1',
                    'format': None
                }
            ]
        }

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
        assert popup_list.get_interactivity() == [
          {
            'event': 'click',
            'attrs': {
                'name': 'v1a58b5',
                'title': 'value_1'
            }
          }, {
            'event': 'click',
            'attrs': {
                'name': 'vbacecf',
                'title': 'value_2'
            }
          }, {
            'event': 'hover',
            'attrs': {
                'name': 'v1a58b5',
                'title': 'value_1'
            }
          }, {
            'event': 'hover',
            'attrs': {
                'name': 'v700930',
                'title': 'value_3'
            }
          }
        ]

    def test_should_get_all_popup_variables(self):
        assert popup_list.get_variables() == {
          'v1a58b5': '$value_1',
          'vbacecf': '$value_2',
          'v1a58b5': '$value_1',
          'v700930': '$value_3'
        }

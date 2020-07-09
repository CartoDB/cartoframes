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
                'name': 'v72224b',
                'title': 'value_2',
                'format': None
            }
          }, {
            'event': 'click',
            'attrs': {
                'name': 'vbc6799',
                'title': 'value_1',
                'format': None
            }
          }, {
            'event': 'hover',
            'attrs': {
                'name': 'vc266e3',
                'title': 'value_3',
                'format': None
            }
          }, {
            'event': 'hover',
            'attrs': {
                'name': 'vbc6799',
                'title': 'value_1',
                'format': None
            }
          }
        ]

    def test_should_get_all_popup_variables(self):
        assert popup_list.get_variables() == {
          'vbc6799': "prop('value_1')",
          'v72224b': "prop('value_2')",
          'vbc6799': "prop('value_1')",
          'vc266e3': "prop('value_3')"
        }

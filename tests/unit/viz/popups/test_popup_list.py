from cartoframes.viz import click_popup, hover_popup, Popup, PopupList

popup_list = PopupList([
  click_popup('value_1'),
  click_popup('value_2'),
  hover_popup('value_1'),
  hover_popup('value_3')
])


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

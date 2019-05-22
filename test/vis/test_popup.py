import unittest
from cartoframes import vis


class TestPopup(unittest.TestCase):
    def test_is_popup_defined(self):
        """vis.Popup"""
        self.assertNotEqual(vis.Popup, None)

    def test_popup_init(self):
        """vis.Popup should be properly initialized"""
        popup = vis.Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'label': 'Pop',
                'value': '$pop'
            }]
        })

        self.assertEqual(popup._click, ['$pop', '$name'])
        self.assertEqual(popup._hover, [{
            'label': 'Pop',
            'value': '$pop'
        }])

    def test_popup_interactivity(self):
        """vis.Popup should return a proper interactivity object"""
        popup = vis.Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'label': 'Pop',
                'value': '$pop'
            }]
        })

        self.assertEqual(popup.get_interactivity(), [{
            'event': 'click',
            'attrs': [{
                'name': 'v559339',
                'label': '$pop'
            }, {
                'name': 'v8e0f74',
                'label': '$name'
            }]
        }, {
            'event': 'hover',
            'attrs': [{
                'name': 'v559339',
                'label': 'Pop'
            }]
        }])

    def test_popup_variables(self):
        """vis.Style should return a proper variables object"""
        popup = vis.Popup({
            'click': ['$pop', '$name'],
            'hover': [{
                'label': 'Pop',
                'value': '$pop'
            }]
        })

        self.assertEqual(popup.get_variables(), {
            'v559339': '$pop',
            'v8e0f74': '$name'
        })

    def test_wrong_attribute(self):
        """vis.Popup should raise an error if popup property is not valid"""
        with self.assertRaises(ValueError):
            vis.Popup(1234)

import unittest

from cartoframes.data.catalog.category import Categories
from cartoframes.data.catalog.country import Countries
from cartoframes.data.catalog.do import DO

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDO(unittest.TestCase):

    expected_countries = [{'iso_code3': 'esp'}, {'iso_code3': 'usa'}]
    expected_categories = [{
        'id': 'cat1',
        'name': 'Financial'
    }, {
        'id': 'cat2',
        'name': 'Demographics'
    }]

    @patch.object(Countries, 'get_all')
    def test_countries(self, mocked_countries):
        # Given
        mocked_countries.return_value = self.expected_countries
        do = DO()

        # When
        countries = do.countries

        # Then
        self.assertEqual(self.expected_countries, countries)

    @patch.object(Categories, 'get_all')
    def test_categories(self, mocked_categories):
        # Given
        mocked_categories.return_value = self.expected_categories
        do = DO()

        # When
        categories = do.categories

        # Then
        self.assertEqual(self.expected_categories, categories)

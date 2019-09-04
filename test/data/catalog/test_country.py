import unittest
import pandas as pd

from cartoframes.data.catalog.country import Countries, Country
from cartoframes.data.catalog.repository.country_repo import CountryRepository

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCountries(unittest.TestCase):

    test_country1 = {'iso_code3': 'esp'}
    test_country2 = {'iso_code3': 'usa'}
    expected_countries = [test_country1, test_country2]

    @patch.object(CountryRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = self.expected_countries

        # When
        countries = Countries.get_all()

        # Then
        assert isinstance(countries, pd.DataFrame)
        assert isinstance(countries, Countries)

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = self.test_country1

        # When
        country = Countries.get_by_id('esp')

        # Then
        assert isinstance(country, pd.Series)
        assert isinstance(country, Country)
import unittest

from cartoframes.data.catalog.repository.country_repo import CountryRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestCountryRepo(unittest.TestCase):

    test_country1 = {'iso_code3': 'esp'}
    test_country2 = {'iso_code3': 'usa'}

    def setUp(self):
        sql_countries = [{
            'country_iso_code3': 'esp'
        }, {
            'country_iso_code3': 'usa'
        }]

        RepoClient.get_countries = Mock(return_value=sql_countries)

    def test_get_all(self):
        # When
        repo = CountryRepository()
        countries = repo.get_all()

        # Then
        expected_countries = [self.test_country1, self.test_country2]
        self.assertEqual(expected_countries, countries)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_countries = Mock(return_value=[])

        # When
        repo = CountryRepository()
        countries = repo.get_all()

        # Then
        self.assertEqual([], countries)

    def test_get_by_iso_code(self):
        # Given
        requested_iso_code = self.test_country1['iso_code3']

        # When
        repo = CountryRepository()
        country = repo.get_by_iso_code(requested_iso_code)

        # Then
        self.assertEqual(self.test_country1, country)

    def test_get_by_iso_code_unknown(self):
        # Given
        RepoClient.get_countries = Mock(return_value=[])
        requested_iso_code = 'fra'

        # When
        repo = CountryRepository()
        country = repo.get_by_iso_code(requested_iso_code)

        # Then
        self.assertEqual(None, country)

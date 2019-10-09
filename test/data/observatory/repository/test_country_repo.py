import unittest

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.country import Country
from cartoframes.data.observatory.repository.country_repo import CountryRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_countries, test_country1, db_country1, db_country2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCountryRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_countries')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_country1, db_country2]
        repo = CountryRepository()

        # When
        countries = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(countries, CatalogList)
        assert countries == test_countries

    @patch.object(RepoClient, 'get_countries')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = CountryRepository()

        # When
        countries = repo.get_all()

        # Then
        assert countries is None

    @patch.object(RepoClient, 'get_countries')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_country1, db_country2]
        requested_iso_code = db_country1['id']
        repo = CountryRepository()

        # When
        country = repo.get_by_id(requested_iso_code)

        # Then
<<<<<<< HEAD
        mocked_repo.assert_called_once_with({'country_id': requested_iso_code})
=======
        mocked_repo.assert_called_once_with('country_id', requested_iso_code)
>>>>>>> develop
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(RepoClient, 'get_countries')
    def test_get_by_iso_code_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_iso_code = 'fra'
        repo = CountryRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_iso_code)

    @patch.object(RepoClient, 'get_countries')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{}]
        repo = CountryRepository()

        expected_countries = CatalogList([Country({
            'id': None
        })])

        # When
        countries = repo.get_all()

        # Then
        assert countries == expected_countries

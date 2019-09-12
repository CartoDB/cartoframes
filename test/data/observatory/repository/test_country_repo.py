import unittest

from cartoframes.data.observatory.country import Countries

from cartoframes.data.observatory.repository.country_repo import CountryRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_countries, test_country1, db_country1, db_country2

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestCountryRepo(unittest.TestCase):

    def setUp(self):
        RepoClient.get_countries = Mock(return_value=[db_country1, db_country2])

    def test_get_all(self):
        # Given
        repo = CountryRepository()

        # When
        countries = repo.all()

        # Then
        assert countries == test_countries

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_countries = Mock(return_value=[])
        repo = CountryRepository()

        # When
        countries = repo.all()

        # Then
        assert countries == Countries([])

    def test_get_by_id(self):
        # Given
        requested_iso_code = test_country1['country_iso_code3']
        repo = CountryRepository()

        # When
        country = repo.by_id(requested_iso_code)

        # Then
        assert country == test_country1

    def test_get_by_iso_code_unknown(self):
        # Given
        RepoClient.get_countries = Mock(return_value=[])
        requested_iso_code = 'fra'
        repo = CountryRepository()

        # When
        country = repo.by_id(requested_iso_code)

        # Then
        assert country is None

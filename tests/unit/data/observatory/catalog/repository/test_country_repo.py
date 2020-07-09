import pytest

from unittest.mock import patch

from cartoframes.exceptions import CatalogError
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.country import Country
from cartoframes.data.observatory.catalog.repository.country_repo import CountryRepository
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from cartoframes.data.observatory.catalog.repository.constants import (
    CATEGORY_FILTER, DATASET_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER, VARIABLE_FILTER,
    VARIABLE_GROUP_FILTER
)
from ..examples import test_countries, test_country1, db_country1, db_country2


class TestCountryRepo(object):

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
        assert countries == []

    @patch.object(RepoClient, 'get_countries')
    def test_get_all_only_uses_allowed_filters(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_country1, db_country2]
        repo = CountryRepository()
        filters = {
            DATASET_FILTER: 'carto-do.project.census2011',
            CATEGORY_FILTER: 'demographics',
            VARIABLE_FILTER: 'population',
            GEOGRAPHY_FILTER: 'census-geo',
            VARIABLE_GROUP_FILTER: 'var-group',
            PROVIDER_FILTER: 'open_data',
            'fake_field_id': 'fake_value'
        }

        # When
        countries = repo.get_all(filters)

        # Then
        mocked_repo.assert_called_once_with({
            CATEGORY_FILTER: 'demographics',
            PROVIDER_FILTER: 'open_data'
        })
        assert countries == test_countries

    @patch.object(RepoClient, 'get_countries')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_country1, db_country2]
        requested_iso_code = db_country1['id']
        repo = CountryRepository()

        # When
        country = repo.get_by_id(requested_iso_code)

        # Then
        mocked_repo.assert_called_once_with({'id': [requested_iso_code]})
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(RepoClient, 'get_countries')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_iso_code = 'fra'
        repo = CountryRepository()

        # Then
        with pytest.raises(CatalogError):
            repo.get_by_id(requested_iso_code)

    @patch.object(RepoClient, 'get_countries')
    def test_get_by_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_country1, db_country2]
        repo = CountryRepository()

        # When
        countries = repo.get_by_id_list([db_country1['id'], db_country2['id']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_country1['id'], db_country2['id']]})
        assert isinstance(countries, CatalogList)
        assert countries == test_countries

    @patch.object(RepoClient, 'get_countries')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{}]
        repo = CountryRepository()

        expected_countries = CatalogList([Country({
            'id': None,
            'name': None
        })])

        # When
        countries = repo.get_all()

        # Then
        assert countries == expected_countries

import pytest

from cartoframes.data.observatory.repository.geography_repo import \
    GeographyRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from cartoframes.exceptions import DiscoveryException

from ..examples import (db_geography1, db_geography2, test_geographies,
                        test_geography1)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestGeographyRepo(object):

    @patch.object(RepoClient, 'get_geographies')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert geographies is None

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        requested_id = test_geography1['id']
        repo = GeographyRepository()

        # When
        geography = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert geography == test_geography1

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = GeographyRepository()

        # Then
        with pytest.raises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        country_code = 'esp'
        repo = GeographyRepository()

        # When
        geography = repo.get_by_country(country_code)

        # Then
        mocked_repo.assert_called_once_with('country_iso_code3', country_code)
        assert geography == test_geographies

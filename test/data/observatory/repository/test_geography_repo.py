import unittest

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.geography import Geography
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_geography1, test_geographies, db_geography1, db_geography2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestGeographyRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_geographies')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert geographies is None

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1]
        requested_id = db_geography1['id']
        repo = GeographyRepository()

        # When
        geography = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': requested_id})
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = GeographyRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_slug(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1]
        requested_slug = db_geography1['slug']
        repo = GeographyRepository()

        # When
        geography = repo.get_by_id(requested_slug)

        # Then
        mocked_repo.assert_called_once_with({'slug': requested_slug})
        assert geography == test_geography1

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_by_id_list([db_geography1['id'], db_geography2['id']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_geography1['id'], db_geography2['id']]})
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_slug_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_by_id_list([db_geography1['slug'], db_geography2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'slug': [db_geography1['slug'], db_geography2['slug']]})
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies')
    def test_get_by_slug_and_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_by_id_list([db_geography1['id'], db_geography2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_geography1['id']], 'slug': [db_geography2['slug']]})
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies_joined_datasets')
    def test_get_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        country_code = 'esp'
        repo = GeographyRepository()

        # When
        geographies = repo.get_by_country(country_code)

        # Then
        mocked_repo.assert_called_once_with({'country_id': country_code})
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies_joined_datasets')
    def test_get_all_with_join_filters(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_geography1, db_geography2]
        repo = GeographyRepository()

        # When
        geographies = repo.get_all({'category_id': 'demographics'})

        # Then
        mocked_repo.assert_called_once_with({'category_id': 'demographics'})
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(RepoClient, 'get_geographies')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'geography1'}]
        repo = GeographyRepository()

        expected_geographies = CatalogList([Geography({
            'id': 'geography1',
            'slug': None,
            'name': None,
            'description': None,
            'provider_id': None,
            'country_id': None,
            'lang': None,
            'geom_coverage': None,
            'update_frequency': None,
            'version': None,
            'is_public_data': None,
            'summary_jsonb': None
        })])

        # When
        geographies = repo.get_all()

        # Then
        assert geographies == expected_geographies

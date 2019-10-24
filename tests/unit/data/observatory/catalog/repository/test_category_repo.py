import pytest

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.catalog.category import Category
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from ..examples import test_category1, test_categories, db_category1, db_category2

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestCategoryRepo(object):

    @patch.object(RepoClient, 'get_categories')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_category1, db_category2]
        repo = CategoryRepository()

        # When
        categories = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(categories, CatalogList)
        assert categories == test_categories

    @patch.object(RepoClient, 'get_categories')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = CategoryRepository()

        # When
        categories = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert categories is None

    @patch.object(RepoClient, 'get_categories_joined_datasets')
    def test_get_all_only_uses_allowed_filters(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_category1, db_category2]
        repo = CategoryRepository()
        filters = {
            'country_id': 'usa',
            'dataset_id': 'carto-do.project.census2011',
            'variable_id': 'population',
            'geography_id': 'census-geo',
            'variable_group_id': 'var-group',
            'provider_id': 'open_data',
            'fake_field_id': 'fake_value'
        }

        # When
        categories = repo.get_all(filters)

        # Then
        mocked_repo.assert_called_once_with({
            'country_id': 'usa'
        })
        assert categories == test_categories

    @patch.object(RepoClient, 'get_categories')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_category1, db_category2]
        requested_id = db_category1['id']
        repo = CategoryRepository()

        # When
        category = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': requested_id})
        assert category == test_category1

    @patch.object(RepoClient, 'get_categories')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = CategoryRepository()

        # Then
        with pytest.raises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_categories')
    def test_get_by_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_category1, db_category2]
        repo = CategoryRepository()

        # When
        categories = repo.get_by_id_list([db_category1['id'], db_category2['id']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_category1['id'], db_category2['id']]})
        assert isinstance(categories, CatalogList)
        assert categories == test_categories

    @patch.object(RepoClient, '_run_query')
    def test_get_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_category1, db_category2]
        country_code = 'esp'
        repo = CategoryRepository()

        # When
        categories = repo.get_all({'country_id': country_code})

        # Then
        query = 'SELECT DISTINCT c.* FROM categories_public c, datasets_public t'
        mocked_repo.assert_called_once_with(query, {'country_id': country_code}, ['c.id = t.category_id'])
        assert isinstance(categories, CatalogList)
        assert categories == test_categories

    @patch.object(RepoClient, 'get_categories')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'cat1'}]
        repo = CategoryRepository()

        expected_categories = CatalogList([Category({
            'id': 'cat1',
            'name': None
        })])

        # When
        categories = repo.get_all()

        # Then
        assert categories == expected_categories

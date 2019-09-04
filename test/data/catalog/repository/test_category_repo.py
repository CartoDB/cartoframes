import unittest

from cartoframes.data.catalog.repository.category_repo import CategoryRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestCategoryRepo(unittest.TestCase):

    test_category1 = {
        'id': 'cat1',
        'name': 'Financial'
    }
    test_category2 = {
        'id': 'cat2',
        'name': 'Demographics'
    }

    def setUp(self):
        mocked_sql_result = [{
            'id': 'cat1',
            'name': 'Financial'
        }, {
            'id': 'cat2',
            'name': 'Demographics'
        }]

        RepoClient.get_categories = Mock(return_value=mocked_sql_result)

    def test_get_all(self):
        # Given
        repo = CategoryRepository()

        # When
        categories = repo.get_all()

        # Then
        expected_categories = [self.test_category1, self.test_category2]
        self.assertEqual(expected_categories, categories)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])
        repo = CategoryRepository()

        # When
        categories = repo.get_all()

        # Then
        assert categories == []

    def test_get_by_id(self):
        # Given
        requested_id = self.test_category1['id']
        repo = CategoryRepository()

        # When
        category = repo.get_by_id(requested_id)

        # Then
        assert category == self.test_category1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])
        requested_id = 'unknown_id'
        repo = CategoryRepository()

        # When
        category = repo.get_by_id(requested_id)

        # Then
        assert category is None
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
        sql_categories = [{
            'id': 'cat1',
            'name': 'Financial'
        }, {
            'id': 'cat2',
            'name': 'Demographics'
        }]

        RepoClient.get_categories = Mock(return_value=sql_categories)

    def test_get_all(self):
        # When
        repo = CategoryRepository()
        categories = repo.get_all()

        # Then
        expected_categories = [self.test_category1, self.test_category2]
        self.assertEqual(expected_categories, categories)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])

        # When
        repo = CategoryRepository()
        categories = repo.get_all()

        # Then
        self.assertEqual([], categories)

    def test_get_by_id(self):
        # Given
        requested_id = self.test_category1['id']

        # When
        repo = CategoryRepository()
        category = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(self.test_category1, category)

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = CategoryRepository()
        category = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(None, category)

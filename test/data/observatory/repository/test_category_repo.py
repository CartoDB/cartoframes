import unittest

from cartoframes.data.observatory.category import Categories

from cartoframes.data.observatory.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_category1, test_categories

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestCategoryRepo(unittest.TestCase):

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
        assert categories == test_categories

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])
        repo = CategoryRepository()

        # When
        categories = repo.get_all()

        # Then
        assert categories == Categories([])

    def test_get_by_id(self):
        # Given
        requested_id = test_category1['id']
        repo = CategoryRepository()

        # When
        category = repo.get_by_id(requested_id)

        # Then
        assert category == test_category1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_categories = Mock(return_value=[])
        requested_id = 'unknown_id'
        repo = CategoryRepository()

        # When
        category = repo.get_by_id(requested_id)

        # Then
        assert category is None

import unittest
import pandas as pd

from cartoframes.data.observatory.category import Category, Categories
from cartoframes.data.observatory.dataset import Datasets

from cartoframes.data.observatory.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_category1, test_datasets, test_categories

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCategory(unittest.TestCase):

    @patch.object(CategoryRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Category.get_by_id('cat1')

        # Then
        assert isinstance(category, pd.Series)
        assert isinstance(category, Category)
        assert category == test_category1

    @patch.object(DatasetRepository, 'by_category')
    def test_get_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_category1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets


class TestCategories(unittest.TestCase):

    @patch.object(CategoryRepository, 'all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = Categories.all()

        # Then
        assert isinstance(categories, pd.DataFrame)
        assert isinstance(categories, Categories)
        assert categories == test_categories

    @patch.object(CategoryRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Categories.get_by_id('cat1')

        # Then
        assert isinstance(category, pd.Series)
        assert isinstance(category, Category)
        assert category == test_category1

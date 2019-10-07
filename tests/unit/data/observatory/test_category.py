import pandas as pd
import pytest

from cartoframes.data.observatory.category import Categories, Category
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.repository.category_repo import \
    CategoryRepository
from cartoframes.data.observatory.repository.dataset_repo import \
    DatasetRepository
from cartoframes.exceptions import DiscoveryException

from .examples import (db_category1, test_categories, test_category1,
                       test_datasets)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestCategory(object):

    @patch.object(CategoryRepository, 'get_by_id')
    def test_get_category_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Category.get_by_id('cat1')

        # Then
        assert isinstance(category, pd.Series)
        assert isinstance(category, Category)
        assert category == test_category1

    @patch.object(DatasetRepository, 'get_by_category')
    def test_get_datasets_by_category(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_category1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_get_datasets_by_category_fails_if_column_Series(self):
        # Given
        category = test_categories.id

        # Then
        with pytest.raises(DiscoveryException):
            category.datasets()


class TestCategories(object):

    @patch.object(CategoryRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = Categories.get_all()

        # Then
        assert isinstance(categories, pd.DataFrame)
        assert isinstance(categories, Categories)
        assert categories == test_categories

    @patch.object(CategoryRepository, 'get_by_id')
    def test_get_category_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Categories.get_by_id('cat1')

        # Then
        assert isinstance(category, pd.Series)
        assert isinstance(category, Category)
        assert category == test_category1

    @patch.object(CategoryRepository, 'get_all')
    def test_categories_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories
        category_id = db_category1['id']

        # When
        categories = Categories.get_all()
        category = categories.loc[category_id]

        # Then
        assert category == test_category1

    @patch.object(CategoryRepository, 'get_all')
    def test_categories_slice_is_category_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = Categories.get_all()
        category = categories.iloc[0]

        # Then
        assert isinstance(category, Category)
        assert isinstance(category, pd.Series)

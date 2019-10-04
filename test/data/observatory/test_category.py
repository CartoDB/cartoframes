import unittest
import pandas as pd

from cartoframes.data.observatory.category import Category

from cartoframes.data.observatory.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.entity import CatalogList

from .examples import test_category1, test_datasets, test_categories, db_category1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCategory(unittest.TestCase):

    @patch.object(CategoryRepository, 'get_by_id')
    def test_get_category_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Category.get('cat1')

        # Then
        assert isinstance(category, object)
        assert isinstance(category, Category)
        assert category == test_category1

    @patch.object(DatasetRepository, 'get_by_category')
    def test_get_datasets_by_category(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_category1.datasets()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    def test_category_properties(self):
        # Given
        category = Category(db_category1)

        # When
        cat_id = category.id
        name = category.name

        # Then
        assert cat_id == db_category1['id']
        assert name == db_category1['name']

    def test_category_is_exported_as_series(self):
        # Given
        category = test_category1

        # When
        category_series = category.to_series()

        # Then
        assert isinstance(category_series, pd.Series)
        assert category_series['id'] == category.id

    @patch.object(CategoryRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = Category.get_all()

        # Then
        assert isinstance(categories, list)
        assert isinstance(categories, CatalogList)
        assert categories == test_categories

    @patch.object(CategoryRepository, 'get_by_id')
    def test_get_category_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_category1

        # When
        category = Category.get('cat1')

        # Then
        assert isinstance(category, object)
        assert isinstance(category, Category)
        assert category == test_category1

    # @patch.object(CategoryRepository, 'get_all')
    # def test_categories_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_categories
    #     category_id = db_category1['id']
    #
    #     # When
    #     categories = Categories.get_all()
    #     category = categories.loc[category_id]
    #
    #     # Then
    #     assert category == test_category1

    def test_categories_items_are_obtained_as_category(self):
        # Given
        categories = test_categories

        # When
        category = categories[0]

        # Then
        assert isinstance(category, Category)
        assert category == test_category1

    def test_categories_are_exported_as_dataframe(self):
        # Given
        categories = test_categories
        category = categories[0]

        # When
        categories_df = categories.to_dataframe()
        sliced_category = categories_df.iloc[0]

        # Then
        assert isinstance(categories_df, pd.DataFrame)
        assert isinstance(sliced_category, pd.Series)
        assert sliced_category.equals(category.to_series())

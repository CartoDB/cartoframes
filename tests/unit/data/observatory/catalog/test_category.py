import pandas as pd

from unittest.mock import patch

from cartoframes.data.observatory.catalog.category import Category
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.repository.constants import CATEGORY_FILTER
from .examples import (
    test_category1, test_datasets, test_categories, db_category1, test_category2, db_category2,
    test_geographies
)


class TestCategory(object):

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

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_category(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_category1.datasets

        # Then
        mocked_repo.assert_called_once_with({CATEGORY_FILTER: test_category1.id})
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(GeographyRepository, 'get_all')
    def test_get_geographies_by_category(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = test_category1.geographies

        # Then
        mocked_repo.assert_called_once_with({CATEGORY_FILTER: test_category1.id})
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

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
        category = Category(db_category1)

        # When
        category_series = category.to_series()

        # Then
        assert isinstance(category_series, pd.Series)
        assert category_series['id'] == category.id

    def test_category_is_exported_as_dict(self):
        # Given
        category = Category(db_category1)

        # When
        category_dict = category.to_dict()

        # Then
        assert isinstance(category_dict, dict)
        assert category_dict == db_category1

    def test_category_is_represented_with_classname_and_id(self):
        # Given
        category = Category(db_category1)

        # When
        category_repr = repr(category)

        # Then
        assert category_repr == "<Category.get('{id}')>".format(id=db_category1['id'])

    def test_category_is_printed_with_classname(self):
        # Given
        category = Category(db_category1)

        # When
        category_str = str(category)

        # Then
        assert category_str == "Category({dict_str})".format(dict_str=str(db_category1))

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

    def test_category_list_is_printed_with_classname_and_ids(self):
        # Given
        categories = CatalogList([test_category1, test_category2])

        # When
        categories_str = str(categories)

        # Then
        assert categories_str == "[<Category.get('{id1}')>, <Category.get('{id2}')>]" \
                                 .format(id1=db_category1['id'], id2=db_category2['id'])

    def test_category_list_is_represented_with_classname_and_ids(self):
        # Given
        categories = CatalogList([test_category1, test_category2])

        # When
        categories_repr = repr(categories)

        # Then
        assert categories_repr == "[<Category.get('{id1}')>, <Category.get('{id2}')>]"\
                                  .format(id1=db_category1['id'], id2=db_category2['id'])

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

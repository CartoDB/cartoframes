import unittest
import pandas as pd

from cartoframes.data.observatory.entity import CatalogList

from cartoframes.data.observatory.variable_group import VariableGroup
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.variable_group_repo import VariableGroupRepository

from .examples import test_variables_groups, test_variable_group1, test_variables, db_variable_group1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariableGroup(unittest.TestCase):

    @patch.object(VariableGroupRepository, 'get_by_id')
    def test_get_variable_group_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable_group1

        # When
        variable_group = VariableGroup.get(test_variable_group1.id)

        # Then
        assert isinstance(variable_group, object)
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    @patch.object(VariableRepository, 'get_by_variable_group')
    def test_get_variables_by_variable_group(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_variable_group1.variables()

        # Then
        assert isinstance(variables, list)
        assert isinstance(variables, CatalogList)
        assert variables == test_variables

    def test_variable_group_properties(self):
        # Given
        variable_group = VariableGroup(db_variable_group1)

        # When
        variable_group_id = variable_group.id
        name = variable_group.name
        dataset = variable_group.dataset
        starred = variable_group.starred

        # Then
        assert variable_group_id == db_variable_group1['id']
        assert name == db_variable_group1['name']
        assert dataset == db_variable_group1['dataset_id']
        assert starred == db_variable_group1['starred']

    def test_variable_group_is_exported_as_series(self):
        # Given
        variable_group = test_variable_group1

        # When
        variable_group_series = variable_group.to_series()

        # Then
        assert isinstance(variable_group_series, pd.Series)
        assert variable_group_series['id'] == variable_group.id


class TestVariablesGroups(unittest.TestCase):

    @patch.object(VariableGroupRepository, 'get_all')
    def test_get_all_variables_groups(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups

        # When
        variables_groups = VariableGroup.get_all()

        # Then
        assert isinstance(variables_groups, list)
        assert isinstance(variables_groups, CatalogList)
        assert variables_groups == test_variables_groups

    @patch.object(VariableGroupRepository, 'get_by_id')
    def test_get_variable_group_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable_group1

        # When
        variable_group = VariableGroup.get(test_variable_group1.id)

        # Then
        assert isinstance(variable_group, object)
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    # @patch.object(VariableGroupRepository, 'get_all')
    # def test_variables_groups_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_variables_groups
    #     variable_group_id = db_variable_group1.id
    #
    #     # When
    #     variables_groups = VariablesGroups.get_all()
    #     variable_group = variables_groups.loc[variable_group_id]
    #
    #     # Then
    #     assert variable_group == test_variable_group1

    def test_variables_groups_items_are_obtained_as_variable_group(self):
        # Given
        variables_groups = test_variables_groups

        # When
        variable_group = variables_groups[0]

        # Then
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    def test_variables_groups_are_exported_as_dataframe(self):
        # Given
        variables_groups = test_variables_groups
        variable_group = variables_groups[0]

        # When
        variable_group_df = variables_groups.to_dataframe()
        sliced_variable_group = variable_group_df.iloc[0]

        # Then
        assert isinstance(variable_group_df, pd.DataFrame)
        assert isinstance(sliced_variable_group, pd.Series)
        assert sliced_variable_group.equals(variable_group.to_series())

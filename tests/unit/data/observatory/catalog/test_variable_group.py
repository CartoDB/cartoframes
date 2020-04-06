import pandas as pd

from unittest.mock import patch

from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.variable_group import VariableGroup
from cartoframes.data.observatory.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.catalog.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.catalog.repository.constants import VARIABLE_GROUP_FILTER
from .examples import (
    test_variables_groups, test_variable_group1, test_variables, db_variable_group1,
    test_variable_group2, db_variable_group2
)


class TestVariableGroup(object):

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

    @patch.object(VariableRepository, 'get_all')
    def test_get_variables_by_variable_group(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_variable_group1.variables

        # Then
        mocked_repo.assert_called_once_with({VARIABLE_GROUP_FILTER: test_variable_group1.id})
        assert isinstance(variables, list)
        assert isinstance(variables, CatalogList)
        assert variables == test_variables

    def test_variable_group_properties(self):
        # Given
        variable_group = VariableGroup(db_variable_group1)

        # When
        variable_group_id = variable_group.id
        slug = variable_group.slug
        name = variable_group.name
        dataset = variable_group.dataset

        # Then
        assert variable_group_id == db_variable_group1['id']
        assert slug == db_variable_group1['slug']
        assert name == db_variable_group1['name']
        assert dataset == db_variable_group1['dataset_id']

    def test_variable_group_is_exported_as_series(self):
        # Given
        variable_group = test_variable_group1

        # When
        variable_group_series = variable_group.to_series()

        # Then
        assert isinstance(variable_group_series, pd.Series)
        assert variable_group_series['id'] == variable_group.id

    def test_variable_group_is_exported_as_dict(self):
        # Given
        variable_group = VariableGroup(db_variable_group1)

        # When
        variable_group_dict = variable_group.to_dict()

        # Then
        assert isinstance(variable_group_dict, dict)
        assert variable_group_dict == db_variable_group1

    def test_variable_group_is_represented_with_classname_and_slug(self):
        # Given
        variable_group = VariableGroup(db_variable_group1)

        # When
        variable_group_repr = repr(variable_group)

        # Then
        assert variable_group_repr == "<VariableGroup.get('{id}')>".format(id=db_variable_group1['slug'])

    def test_variable_group_is_printed_with_classname(self):
        # Given
        variable_group = VariableGroup(db_variable_group1)

        # When
        variable_group_str = str(variable_group)

        # Then
        assert variable_group_str == 'VariableGroup({dict_str})'.format(dict_str=str(db_variable_group1))

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

    def test_variable_group_list_is_printed_with_classname_and_slug(self):
        # Given
        variables_groups = CatalogList([test_variable_group1, test_variable_group2])

        # When
        variables_groups_str = str(variables_groups)

        # Then
        assert variables_groups_str == "[<VariableGroup.get('{id1}')>, <VariableGroup.get('{id2}')>]" \
                                       .format(id1=db_variable_group1['slug'], id2=db_variable_group2['slug'])

    def test_variable_group_list_is_represented_with_classname_and_slug(self):
        # Given
        variables_groups = CatalogList([test_variable_group1, test_variable_group2])

        # When
        variables_groups_repr = repr(variables_groups)

        # Then
        assert variables_groups_repr == "[<VariableGroup.get('{id1}')>, <VariableGroup.get('{id2}')>]"\
                                        .format(id1=db_variable_group1['slug'], id2=db_variable_group2['slug'])

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

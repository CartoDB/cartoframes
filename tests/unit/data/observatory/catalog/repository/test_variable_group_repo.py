import pytest

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.variable_group import VariableGroup
from cartoframes.data.observatory.catalog.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from ..examples import test_variable_group1, test_variables_groups, db_variable_group1, db_variable_group2

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestVariableGroupRepo(object):

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(variables_groups, CatalogList)
        assert variables_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []

        # When
        repo = VariableGroupRepository()
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert variables_groups is None

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all_only_uses_allowed_filters(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()
        filters = {
            'country_id': 'usa',
            'dataset_id': 'carto-do.project.census2011',
            'category_id': 'demographics',
            'variable_id': 'population',
            'geography_id': 'census-geo',
            'variable_group_id': 'var-group',
            'provider_id': 'open_data',
            'fake_field_id': 'fake_value'
        }

        # When
        variables_groups = repo.get_all(filters)

        # Then
        mocked_repo.assert_called_once_with({
            'dataset_id': 'carto-do.project.census2011'
        })
        assert variables_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        requested_id = db_variable_group1['id']

        # When
        repo = VariableGroupRepository()
        variable_group = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': requested_id})
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = VariableGroupRepository()

        # Then
        with pytest.raises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_slug(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1]
        requested_slug = db_variable_group1['slug']
        repo = VariableGroupRepository()

        # When
        variable = repo.get_by_id(requested_slug)

        # Then
        mocked_repo.assert_called_once_with({'slug': requested_slug})
        assert variable == test_variable_group1

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variable_groups = repo.get_by_id_list([db_variable_group1['id'], db_variable_group2['id']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_variable_group1['id'], db_variable_group2['id']]})
        assert isinstance(variable_groups, CatalogList)
        assert variable_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_slug_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variable_groups = repo.get_by_id_list([db_variable_group1['slug'], db_variable_group2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'slug': [db_variable_group1['slug'], db_variable_group2['slug']]})
        assert isinstance(variable_groups, CatalogList)
        assert variable_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_slug_and_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variable_groups = repo.get_by_id_list([db_variable_group1['id'], db_variable_group2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_variable_group1['id']], 'slug': [db_variable_group2['slug']]})
        assert isinstance(variable_groups, CatalogList)
        assert variable_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'variable_group1'}]
        repo = VariableGroupRepository()

        expected_variables_groups = CatalogList([VariableGroup({
            'id': 'variable_group1',
            'slug': None,
            'name': None,
            'dataset_id': None,
            'starred': None
        })])

        # When
        variables_groups = repo.get_all()

        # Then
        assert variables_groups == expected_variables_groups

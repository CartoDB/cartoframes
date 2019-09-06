import unittest

from cartoframes.data.catalog.variable import Variables

from cartoframes.data.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient
from data.catalog.examples import test_variable1, test_variables

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestVariableRepo(unittest.TestCase):

    def setUp(self):
        mocked_sql_result = [{
            'id': 'var1',
            'name': 'Population',
            'variable_group_id': 'vargroup1'
        }, {
            'id': 'var2',
            'name': 'Date',
            'variable_group_id': 'vargroup1'
        }]

        RepoClient.get_variables = Mock(return_value=mocked_sql_result)

    def test_get_all(self):
        # Given
        repo = VariableRepository()

        # When
        variables = repo.get_all()

        # Then
        assert variables == test_variables

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])

        # When
        repo = VariableRepository()
        variables = repo.get_all()

        # Then
        assert variables == Variables([])

    def test_get_by_id(self):
        # Given
        requested_id = test_variable1['id']

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        assert variable == test_variable1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        assert variable is None

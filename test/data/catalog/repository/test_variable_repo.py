import unittest

from cartoframes.data.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestVariableRepo(unittest.TestCase):

    test_variable1 = {
        'id': 'var1',
        'name': 'Population',
        'group_id': 'vargroup1'
    }
    test_variable2 = {
        'id': 'var2',
        'name': 'Date',
        'group_id': 'vargroup1'
    }

    def setUp(self):
        sql_variables = [{
            'id': 'var1',
            'name': 'Population',
            'group_id': 'vargroup1'
        }, {
            'id': 'var2',
            'name': 'Date',
            'group_id': 'vargroup1'
        }]

        RepoClient.get_variables = Mock(return_value=sql_variables)

    def test_get_all(self):
        # When
        repo = VariableRepository()
        variables = repo.get_all()

        # Then
        expected_variables = [self.test_variable1, self.test_variable2]
        self.assertEqual(expected_variables, variables)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])

        # When
        repo = VariableRepository()
        variables = repo.get_all()

        # Then
        self.assertEqual([], variables)

    def test_get_by_id(self):
        # Given
        requested_id = self.test_variable1['id']

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(self.test_variable1, variable)

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(None, variable)

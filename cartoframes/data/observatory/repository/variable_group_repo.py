from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_variable_group_repo():
    return _REPO


class VariableGroupRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_variables_groups(self.client.get_variables_groups())

    def get_by_id(self, variable_group_id):
        result = self.client.get_variables_groups('id', variable_group_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing variable group in the catalog. '
                                     'You can check the full list of available variables with VariableGroups.get_all()')

        return self._to_variable_group(result[0])

    def get_by_dataset(self, dataset_id):
        return self._to_variables_groups(self.client.get_variables_groups('dataset_id', dataset_id))

    @staticmethod
    def _to_variable_group(result):
        from cartoframes.data.observatory.variable_group import VariableGroup

        return VariableGroup(result)

    @staticmethod
    def _to_variables_groups(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.variable_group import VariablesGroups

        return VariablesGroups([VariableGroupRepository._to_variable_group(result) for result in results])


_REPO = VariableGroupRepository()

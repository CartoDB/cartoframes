from data.catalog.repository.repo_client import RepoClient


def get_variable_repo():
    return VariableRepository()


class VariableRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return [self._to_variable(result) for result in self.client.get_variables()]

    def get_by_id(self, variable_id):
        result = self.client.get_variables('id', variable_id)[0]
        return self._to_variable(result)

    @staticmethod
    def _to_variable(result):
        return {
            'id': result['id'],
            'name': result['name'],
            'group_id': result['group_id']
        }

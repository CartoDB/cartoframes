from cartoframes.data.observatory.repository.repo_client import RepoClient


def get_variable_repo():
    return VariableRepository()


class VariableRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_variables(self.client.get_variables())

    def get_by_id(self, variable_id):
        result = self.client.get_variables('id', variable_id)

        if len(result) == 0:
            return None

        return self._to_variable(result[0])

    def get_by_dataset(self, dataset_id):
        return self._to_variables(self.client.get_variables('dataset_id', dataset_id))

    @staticmethod
    def _to_variable(result):
        from cartoframes.data.observatory.variable import Variable

        return Variable({
            'id': result['id'],
            'name': result['name'],
            'group_id': result['variable_group_id']
        })

    @staticmethod
    def _to_variables(results):
        from cartoframes.data.observatory.variable import Variables

        return Variables([VariableRepository._to_variable(result) for result in results])

from .repo_client import RepoClient


def get_variable_repo():
    return _REPO


class VariableRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def all(self):
        return self._to_variables(self.client.get_variables())

    def by_id(self, variable_id):
        result = self.client.get_variables('id', variable_id)

        if len(result) == 0:
            return None

        return self._to_variable(result[0])

    def by_dataset(self, dataset_id):
        return self._to_variables(self.client.get_variables('dataset_id', dataset_id))

    @staticmethod
    def _to_variable(result):
        from cartoframes.data.observatory.variable import Variable

        return Variable(result)

    @staticmethod
    def _to_variables(results):
        from cartoframes.data.observatory.variable import Variables

        return Variables([VariableRepository._to_variable(result) for result in results])


_REPO = VariableRepository()

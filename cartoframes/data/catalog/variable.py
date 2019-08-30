from data.catalog.repository.dataset_repo import get_dataset_repo
from data.catalog.repository.variable_repo import get_variable_repo


def get_variables():
    return [Variable(var) for var in get_variable_repo().get_all()]


class Variable(object):

    def __init__(self, metadata):
        self.id = metadata.id
        self.name = metadata.name
        self.group_id = metadata.group_id

    @staticmethod
    def get(variable_id):
        metadata = get_variable_repo().get_by_id(variable_id)
        return Variable(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_variable(self.id)

from data.catalog.repository.dataset_repo import get_dataset_repo
from data.catalog.repository.variable_repo import get_variable_repo


class Variable(object):

    def __init__(self, metadata):
        # TODO: Confirm which properties from the DDL we should include here
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


class Variables(list):

    def __init__(self, items):
        super(Variables, self).__init__(items)

    @staticmethod
    def get_all():
        return [Variable(var) for var in get_variable_repo().get_all()]

    @staticmethod
    def get(variable_id):
        return Variable.get(variable_id)

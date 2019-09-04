import pandas as pd
from data.catalog.repository.dataset_repo import get_dataset_repo
from data.catalog.repository.variable_repo import get_variable_repo


class Variable(pd.Series):

    def __init__(self, variable):
        super(Variable, self).__init__(variable)

    @staticmethod
    def get_by_id(variable_id):
        metadata = get_variable_repo().get_by_id(variable_id)
        return Variable(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_variable(self.id)


class Variables(pd.DataFrame):

    def __init__(self, items):
        super(Variables, self).__init__(items)

    @staticmethod
    def get_all():
        return Variables([Variable(var) for var in get_variable_repo().get_all()])

    @staticmethod
    def get_by_id(variable_id):
        return Variable.get_by_id(variable_id)

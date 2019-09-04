import pandas as pd
from data.catalog.repository.dataset_repo import get_dataset_repo
from data.catalog.repository.variable_repo import get_variable_repo

_VARIABLE_FIELD_ID = 'id'


class Variable(pd.Series):

    @property
    def _constructor(self):
        return Variable

    @property
    def _constructor_expanddim(self):
        return Variables

    @staticmethod
    def get_by_id(variable_id):
        metadata = get_variable_repo().get_by_id(variable_id)
        return Variable(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_variable(self[_VARIABLE_FIELD_ID])


class Variables(pd.DataFrame):

    @property
    def _constructor(self):
        return Variables

    @property
    def _constructor_sliced(self):
        return Variable

    @staticmethod
    def get_all():
        return Variables([Variable(var) for var in get_variable_repo().get_all()])

    @staticmethod
    def get_by_id(variable_id):
        return Variable.get_by_id(variable_id)

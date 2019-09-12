import pandas as pd

from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_FIELD_ID = 'id'


class Variable(pd.Series):

    @property
    def _constructor(self):
        return Variable

    @property
    def _constructor_expanddim(self):
        return Variables

    @staticmethod
    def by_id(variable_id):
        return get_variable_repo().by_id(variable_id)

    def datasets(self):
        return get_dataset_repo().by_variable(self[_VARIABLE_FIELD_ID])

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Variables(pd.DataFrame):

    @property
    def _constructor(self):
        return Variables

    @property
    def _constructor_sliced(self):
        return Variable

    @staticmethod
    def all():
        return get_variable_repo().all()

    @staticmethod
    def by_id(variable_id):
        return Variable.by_id(variable_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

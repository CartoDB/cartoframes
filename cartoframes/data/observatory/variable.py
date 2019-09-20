import pandas as pd

from cartoframes.exceptions import DiscoveryException
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_ID_FIELD = 'id'


class Variable(pd.Series):

    @property
    def _constructor(self):
        return Variable

    @property
    def _constructor_expanddim(self):
        return Variables

    @staticmethod
    def get_by_id(variable_id):
        return get_variable_repo().get_by_id(variable_id)

    def datasets(self):
        return get_dataset_repo().get_by_variable(self.get_id())

    def get_id(self):
        try:
            return self[_VARIABLE_ID_FIELD]
        except KeyError:
            raise DiscoveryException('Unsupported function: this Series represents a column, not a row')

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

    def __init__(self, data):
        super(Variables, self).__init__(data)
        self.set_index(_VARIABLE_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_variable_repo().get_all()

    @staticmethod
    def get_by_id(variable_id):
        return Variable.get_by_id(variable_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

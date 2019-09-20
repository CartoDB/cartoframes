import pandas as pd

from cartoframes.exceptions import DiscoveryException
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo

_DATASET_ID_FIELD = 'id'


class Dataset(pd.Series):

    @property
    def _constructor(self):
        return Dataset

    @property
    def _constructor_expanddim(self):
        return Datasets

    @staticmethod
    def get_by_id(dataset_id):
        return get_dataset_repo().get_by_id(dataset_id)

    def variables(self):
        return get_variable_repo().get_by_dataset(self._get_id())

    def _get_id(self):
        try:
            return self[_DATASET_ID_FIELD]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of Datasets '
                                     'class. You should use `Datasets.get_by_id("dataset_id")` to obtain a valid '
                                     'instance of the Dataset class and then attempt this function on it.')

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Datasets(pd.DataFrame):

    @property
    def _constructor(self):
        return Datasets

    @property
    def _constructor_sliced(self):
        return Dataset

    def __init__(self, data):
        super(Datasets, self).__init__(data)
        self.set_index(_DATASET_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_dataset_repo().get_all()

    @staticmethod
    def get_by_id(dataset_id):
        return Dataset.get_by_id(dataset_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

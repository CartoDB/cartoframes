import pandas as pd

from cartoframes.exceptions import DiscoveryException
from .repository.provider_repo import get_provider_repo
from .repository.dataset_repo import get_dataset_repo


_PROVIDER_ID_FIELD = 'id'


class Provider(pd.Series):

    @property
    def _constructor(self):
        return Provider

    @property
    def _constructor_expanddim(self):
        return Providers

    @staticmethod
    def get_by_id(provider_id):
        return get_provider_repo().get_by_id(provider_id)

    def datasets(self):
        return get_dataset_repo().get_by_provider(self._get_id())

    def _get_id(self):
        try:
            return self[_PROVIDER_ID_FIELD]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of Providers '
                                     'class. You should use `Providers.get_by_id("category_id")` to obtain a valid '
                                     'instance of the Provider class and then attempt this function on it.')

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Providers(pd.DataFrame):

    @property
    def _constructor(self):
        return Providers

    @property
    def _constructor_sliced(self):
        return Provider

    def __init__(self, data):
        super(Providers, self).__init__(data)
        self.set_index(_PROVIDER_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_provider_repo().get_all()

    @staticmethod
    def get_by_id(category_id):
        return Provider.get_by_id(category_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

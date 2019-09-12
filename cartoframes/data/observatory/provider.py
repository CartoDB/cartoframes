import pandas as pd

from cartoframes.data.observatory.repository.provider_repo import get_provider_repo
from cartoframes.data.observatory.repository.dataset_repo import get_dataset_repo


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
        return get_provider_repo().by_id(provider_id)

    def datasets(self):
        return get_dataset_repo().by_provider(self[_PROVIDER_ID_FIELD])

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

    @staticmethod
    def all():
        return get_provider_repo().all()

    @staticmethod
    def get_by_id(category_id):
        return Provider.get_by_id(category_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

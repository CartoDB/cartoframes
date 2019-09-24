import pandas as pd

from cartoframes.exceptions import DiscoveryException
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo

_COUNTRY_ID_FIELD = 'country_iso_code3'


class Country(pd.Series):

    @property
    def _constructor(self):
        return Country

    @property
    def _constructor_expanddim(self):
        return Countries

    @staticmethod
    def get_by_id(iso_code3):
        return get_country_repo().get_by_id(iso_code3)

    def datasets(self):
        return get_dataset_repo().get_by_country(self._get_id())

    def geographies(self):
        return get_geography_repo().get_by_country(self._get_id())

    def _get_id(self):
        try:
            return self[_COUNTRY_ID_FIELD]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of Countries '
                                     'class. You should use `Countries.get_by_id("country_id")` to obtain a valid '
                                     'instance of the Country class and then attempt this function on it.')

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Countries(pd.DataFrame):

    @property
    def _constructor(self):
        return Countries

    @property
    def _constructor_sliced(self):
        return Country

    def __init__(self, data):
        super(Countries, self).__init__(data)
        self.set_index(_COUNTRY_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_country_repo().get_all()

    @staticmethod
    def get_by_id(iso_code3):
        return Country.get_by_id(iso_code3)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

import pandas as pd
from .repository.geography_repo import get_geography_repo
from .repository.category_repo import get_category_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo

_COUNTRY_ID_FIELD = 'iso_code3'


class Country(pd.Series):

    @property
    def _constructor(self):
        return Country

    @property
    def _constructor_expanddim(self):
        return Countries

    @staticmethod
    def get_by_id(iso_code3):
        return Country(get_country_repo().get_by_id(iso_code3))

    @property
    def datasets(self):
        return get_dataset_repo().get_by_country(self[_COUNTRY_ID_FIELD])

    @property
    def categories(self):
        return get_category_repo().get_by_country(self[_COUNTRY_ID_FIELD])

    @property
    def geographies(self):
        return get_geography_repo().get_by_country(self[_COUNTRY_ID_FIELD])


class Countries(pd.DataFrame):

    @property
    def _constructor(self):
        return Countries

    @property
    def _constructor_sliced(self):
        return Country

    @staticmethod
    def get_all():
        return Countries([Country(country) for country in get_country_repo().get_all()])

    @staticmethod
    def get_by_id(iso_code3):
        return Country.get_by_id(iso_code3)

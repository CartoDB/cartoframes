import pandas as pd
from .repository.geography_repo import get_geography_repo
from .repository.category_repo import get_category_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo


class Country(pd.Series):

    def __init__(self, country):
        super(Country, self).__init__(country)

    @staticmethod
    def get_by_id(iso_code3):
        return Country(get_country_repo().get_by_iso_code(iso_code3))

    @property
    def datasets(self):
        return get_dataset_repo().get_by_country(self.iso_code3)

    @property
    def categories(self):
        return get_category_repo().get_by_country(self.iso_code3)

    @property
    def geographies(self):
        return get_geography_repo().get_by_country(self.iso_code3)


class Countries(pd.DataFrame):

    def __init__(self, items):
        super(Countries, self).__init__(items)

    @staticmethod
    def get_all():
        return Countries([Country(country) for country in get_country_repo().get_all()])

    @staticmethod
    def get_by_id(iso_code3):
        return Country.get_by_id(iso_code3)

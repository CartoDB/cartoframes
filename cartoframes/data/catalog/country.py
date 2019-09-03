from .repository.geography_repo import get_geography_repo
from .repository.category_repo import get_category_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo


class Country(object):

    def __init__(self, metadata):
        self.iso_code3 = metadata.iso_code3

    @staticmethod
    def get(iso_code3):
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


class Countries(list):

    def __init__(self, items):
        super(Countries, self).__init__(items)

    @staticmethod
    def get_all():
        return [Country(country) for country in get_country_repo().get_all()]

    @staticmethod
    def get(iso_code3):
        return Country.get(iso_code3)

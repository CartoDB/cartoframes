from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo


def get_countries():
    return [Country(iso_code) for iso_code in get_country_repo().get_all()]


class Country(object):

    def __init__(self, iso_code):
        self.iso_code = iso_code

    @staticmethod
    def get(iso_code):
        return Country(get_country_repo().get_by_iso_code(iso_code))

    @property
    def datasets(self):
        return get_dataset_repo().get_by_country(self.iso_code)

from data.catalog.country import Country
from data.catalog.repo import Repository


class DO(object):

    def __init__(self):
        self.repo = Repository()

    @staticmethod
    def countries(self):
        return [Country(country['country_iso_code3'] for country in self.repo.get_countries())]

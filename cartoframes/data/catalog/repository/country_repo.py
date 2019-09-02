from .repo_client import RepoClient


def get_country_repo():
    return CountryRepository()


class CountryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return [self._to_country(result) for result in self.client.get_countries()]

    def get_by_iso_code(self, iso3):
        result = self.client.get_countries('country_iso_code3', iso3)[0]
        return self._to_country(result)

    @staticmethod
    def _to_country(result):
        # TODO: what if result is empty? What should we return then? And what should the caller do with that?
        return result['country_iso_code3']

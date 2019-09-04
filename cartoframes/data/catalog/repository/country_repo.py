from .repo_client import RepoClient


def get_country_repo():
    return CountryRepository()


class CountryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return [self._to_country(result) for result in self.client.get_countries()]

    def get_by_id(self, iso_code3):
        result = self.client.get_countries('country_iso_code3', iso_code3)

        if len(result) == 0:
            return None

        return self._to_country(result[0])

    @staticmethod
    def _to_country(result):
        return {
            'iso_code3': result['country_iso_code3']
        }

from .repo_client import RepoClient


def get_country_repo():
    return _REPO


class CountryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def all(self):
        return self._to_countries(self.client.get_countries())

    def by_id(self, iso_code3):
        result = self.client.get_countries('country_iso_code3', iso_code3)

        if len(result) == 0:
            return None

        return self._to_country(result[0])

    @staticmethod
    def _to_country(result):
        from cartoframes.data.observatory.country import Country

        return Country(result)

    @staticmethod
    def _to_countries(results):
        from cartoframes.data.observatory.country import Countries

        return Countries([CountryRepository._to_country(result) for result in results])


_REPO = CountryRepository()

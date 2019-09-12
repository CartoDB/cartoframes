from .repo_client import RepoClient


def get_geography_repo():
    return _REPO


class GeographyRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def all(self):
        return self._to_geographies(self.client.get_geographies())

    def by_id(self, geography_id):
        result = self.client.get_geographies('id', geography_id)

        if len(result) == 0:
            return None

        return self._to_geography(result[0])

    def by_country(self, iso_code3):
        return self._to_geographies(self.client.get_geographies('country_iso_code3', iso_code3))

    @staticmethod
    def _to_geography(result):
        from cartoframes.data.observatory.geography import Geography

        return Geography(result)

    @staticmethod
    def _to_geographies(results):
        from cartoframes.data.observatory.geography import Geographies

        return Geographies(GeographyRepository._to_geography(result) for result in results)


_REPO = GeographyRepository()

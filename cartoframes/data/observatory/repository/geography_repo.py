from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_geography_repo():
    return _REPO


class GeographyRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_geographies(self.client.get_geographies())

    def get_by_id(self, geography_id):
        result = self.client.get_geographies('id', geography_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing geography in the catalog. '
                                     'You can check the full list of available geographies with Geographies.get_all()')

        return self._to_geography(result[0])

    def get_by_country(self, iso_code3):
        return self._to_geographies(self.client.get_geographies('country_iso_code3', iso_code3))

    @staticmethod
    def _to_geography(result):
        from cartoframes.data.observatory.geography import Geography

        return Geography(result)

    @staticmethod
    def _to_geographies(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.geography import Geographies

        return Geographies(GeographyRepository._to_geography(result) for result in results)


_REPO = GeographyRepository()

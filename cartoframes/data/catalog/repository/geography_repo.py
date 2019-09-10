from cartoframes.data.catalog.repository.repo_client import RepoClient


def get_geography_repo():
    return GeographyRepository()


class GeographyRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_geographies(self.client.get_geographies())

    def get_by_id(self, geography_id):
        result = self.client.get_geographies('id', geography_id)

        if len(result) == 0:
            return None

        return self._to_geography(result[0])

    def get_by_country(self, iso_code):
        # TODO
        pass

    @staticmethod
    def _to_geography(result):
        from cartoframes.data.catalog.geography import Geography

        return Geography({
            'id': result['id'],
            'name': result['name'],
            'provider_id': result['provider_id'],
            'country_iso_code3': result['country_iso_code3'],
            'version': result['version'],
            'is_public': result['is_public_data']
        })

    @staticmethod
    def _to_geographies(results):
        from cartoframes.data.catalog.geography import Geographies

        return Geographies(GeographyRepository._to_geography(result) for result in results)

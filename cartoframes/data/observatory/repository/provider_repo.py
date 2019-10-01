from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_provider_repo():
    return _REPO


class ProviderRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_providers(self.client.get_providers())

    def get_by_id(self, provider_id):
        result = self.client.get_providers('id', provider_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing provider in the catalog. '
                                     'You can check the full list of available providers with Providers.get_all()')

        return self._to_provider(result[0])

    @staticmethod
    def _to_provider(result):
        from cartoframes.data.observatory.provider import Provider

        return Provider({
            'id': result['id'],
            'name': result['name']
        })

    @staticmethod
    def _to_providers(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.provider import Providers

        return Providers([ProviderRepository._to_provider(result) for result in results])


_REPO = ProviderRepository()

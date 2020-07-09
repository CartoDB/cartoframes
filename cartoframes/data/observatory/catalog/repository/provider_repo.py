from .constants import CATEGORY_FILTER, COUNTRY_FILTER, PUBLIC_FILTER
from .entity_repo import EntityRepository


_PROVIDER_ID_FIELD = 'id'
_ALLOWED_FILTERS = [CATEGORY_FILTER, COUNTRY_FILTER, PUBLIC_FILTER]


def get_provider_repo():
    return _REPO


class ProviderRepository(EntityRepository):

    def __init__(self):
        super(ProviderRepository, self).__init__(_PROVIDER_ID_FIELD, _ALLOWED_FILTERS)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.provider import Provider
        return Provider

    def _get_rows(self, filters=None):
        return self.client.get_providers(filters)

    def _map_row(self, row):
        return {
           'id': self._normalize_field(row, self.id_field),
           'name': self._normalize_field(row, 'name')
        }


_REPO = ProviderRepository()

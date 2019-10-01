from .entity_repo import EntityRepository


_PROVIDER_ID_FIELD = 'id'


def get_provider_repo():
    return _REPO


class ProviderRepository(EntityRepository):

    id_field = _PROVIDER_ID_FIELD

    @classmethod
    def _map_row(cls, row):
        return {
           'id': cls._normalize_field(row, cls.id_field),
           'name': cls._normalize_field(row, 'name')
        }

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.provider import Provider
        return Provider

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.provider import Providers
        return Providers

    def _get_rows(self, field=None, value=None):
        return self.client.get_providers(field, value)


_REPO = ProviderRepository()

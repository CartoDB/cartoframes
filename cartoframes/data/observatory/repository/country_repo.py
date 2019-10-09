from __future__ import absolute_import

from .entity_repo import EntityRepository


_COUNTRY_ID_FIELD = 'country_id'


def get_country_repo():
    return _REPO


class CountryRepository(EntityRepository):

    id_field = _COUNTRY_ID_FIELD

    @classmethod
    def _map_row(cls, row):
        return {
            'id': cls._normalize_field(row, 'id'),
        }

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.country import Country
        return Country

    def _get_rows(self, field=None, value=None):
        return self.client.get_countries(field, value)


_REPO = CountryRepository()

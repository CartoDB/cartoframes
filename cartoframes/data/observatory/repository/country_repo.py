from __future__ import absolute_import

from .constants import CATEGORY_FILTER
from .entity_repo import EntityRepository


_COUNTRY_ID_FIELD = 'country_id'
_ALLOWED_FILTERS = [CATEGORY_FILTER]


def get_country_repo():
    return _REPO


class CountryRepository(EntityRepository):

    def __init__(self):
        super(CountryRepository, self).__init__(_COUNTRY_ID_FIELD, _ALLOWED_FILTERS)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.country import Country
        return Country

    def _get_rows(self, filters=None):
        return self.client.get_countries(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, 'id'),
        }


_REPO = CountryRepository()

from __future__ import absolute_import

from .constants import COUNTRY_FILTER, CATEGORY_FILTER
from .entity_repo import EntityRepository


_GEOGRAPHY_ID_FIELD = 'id'
_ALLOWED_FILTERS = [COUNTRY_FILTER, CATEGORY_FILTER]


def get_geography_repo():
    return _REPO


class GeographyRepository(EntityRepository):

    def __init__(self):
        super(GeographyRepository, self).__init__(_GEOGRAPHY_ID_FIELD, _ALLOWED_FILTERS)

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities({'country_id': iso_code3})

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.geography import Geography
        return Geography

    def _get_rows(self, filters=None):
        if filters is not None and (COUNTRY_FILTER or COUNTRY_FILTER) in filters.keys():
            return self.client.get_geographies_joined_datasets(filters)

        return self.client.get_geographies(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'country_id': self._normalize_field(row, 'country_id'),
            'lang': self._normalize_field(row, 'lang'),
            'geom_coverage': self._normalize_field(row, 'geom_coverage'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'version': self._normalize_field(row, 'version'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'summary_jsonb': self._normalize_field(row, 'summary_jsonb')
        }


_REPO = GeographyRepository()

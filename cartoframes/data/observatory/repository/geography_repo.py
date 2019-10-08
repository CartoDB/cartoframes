from __future__ import absolute_import

from .entity_repo import EntityRepository


_GEOGRAPHY_ID_FIELD = 'id'


def get_geography_repo():
    return _REPO


class GeographyRepository(EntityRepository):

    id_field = _GEOGRAPHY_ID_FIELD

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities({'country_iso_code3': iso_code3})

    @classmethod
    def _map_row(cls, row):
        return {
            'id': cls._normalize_field(row, cls.id_field),
            'name': cls._normalize_field(row, 'name'),
            'description': cls._normalize_field(row, 'description'),
            'provider_id': cls._normalize_field(row, 'provider_id'),
            'country_iso_code3': cls._normalize_field(row, 'country_iso_code3'),
            'language_iso_code3': cls._normalize_field(row, 'language_iso_code3'),
            'geom_coverage': cls._normalize_field(row, 'geom_coverage'),
            'update_frequency': cls._normalize_field(row, 'update_frequency'),
            'version': cls._normalize_field(row, 'version'),
            'is_public_data': cls._normalize_field(row, 'is_public_data'),
            'summary_jsonb': cls._normalize_field(row, 'summary_jsonb')
        }

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.geography import Geography
        return Geography

    def _get_rows(self, filters=None):
        return self.client.get_geographies(filters)


_REPO = GeographyRepository()

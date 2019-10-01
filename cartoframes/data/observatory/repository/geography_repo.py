from .entity_repo import EntityRepository


_GEOGRAPHY_ID_FIELD = 'id'


def get_geography_repo():
    return _REPO


class GeographyRepository(EntityRepository):

    id_field = _GEOGRAPHY_ID_FIELD

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities('country_iso_code3', iso_code3)

    @classmethod
    def _map_row(cls, row):
        return {
            'id': row[cls.id_field],
            'name': row['name'],
            'description': row['description'],
            'provider_id': row['provider_id'],
            'country_iso_code3': row['country_iso_code3'],
            'language_iso_code3': row['language_iso_code3'],
            'geom_coverage': row['geom_coverage'],
            'update_frequency': row['update_frequency'],
            'version': row['version'],
            'is_public_data': row['is_public_data'],
            'summary_jsonb': row['summary_jsonb']
        }

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.geography import Geography
        return Geography

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.geography import Geographies
        return Geographies

    def _get_rows(self, field=None, value=None):
        return self.client.get_geographies(field, value)


_REPO = GeographyRepository()

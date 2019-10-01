from .entity_repo import EntityRepository

_COUNTRY_ID_FIELD = 'country_iso_code3'


def get_country_repo():
    return _REPO


class CountryRepository(EntityRepository):

    id_field = _COUNTRY_ID_FIELD

    @classmethod
    def _map_row(cls, row):
        return {
            'country_iso_code3': row[cls.id_field],
        }

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.country import Country
        return Country

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.country import Countries
        return Countries

    def _get_rows(self, field=None, value=None):
        return self.client.get_countries(field, value)


_REPO = CountryRepository()

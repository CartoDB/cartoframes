from geopandas import GeoDataFrame

from .....utils.geom_utils import set_geometry
from .constants import COUNTRY_FILTER, CATEGORY_FILTER, PROVIDER_FILTER, PUBLIC_FILTER
from .entity_repo import EntityRepository

GEOGRAPHY_TYPE = 'geography'

_GEOGRAPHY_ID_FIELD = 'id'
_GEOGRAPHY_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [COUNTRY_FILTER, CATEGORY_FILTER, PROVIDER_FILTER, PUBLIC_FILTER]


def get_geography_repo():
    return _REPO


class GeographyRepository(EntityRepository):

    def __init__(self):
        super(GeographyRepository, self).__init__(_GEOGRAPHY_ID_FIELD, _ALLOWED_FILTERS, _GEOGRAPHY_SLUG_FIELD)

    def get_all(self, filters=None, credentials=None):
        if credentials is not None:
            filters = self._add_subscription_ids(filters, credentials, GEOGRAPHY_TYPE)
            if filters is None:
                return []

        # Using user credentials to fetch entities
        self.client.set_user_credentials(credentials)
        entities = self._get_filtered_entities(filters)
        self.client.reset_user_credentials()
        return entities

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.geography import Geography
        return Geography

    def _get_rows(self, filters=None):
        return self.client.get_geographies(filters)

    def _map_row(self, row):
        return {
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'country_id': self._normalize_field(row, 'country_id'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'geom_type': self._normalize_field(row, 'geom_type'),
            'geom_coverage': self._normalize_field(row, 'geom_coverage'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'lang': self._normalize_field(row, 'lang'),
            'version': self._normalize_field(row, 'version'),
            'provider_name': self._normalize_field(row, 'provider_name'),
            'summary_json': self._normalize_field(row, 'summary_json'),
            'id': self._normalize_field(row, self.id_field)
        }

    def get_geographies_gdf(self):
        data = self.client.get_geographies({'get_geoms_coverage': True})
        gdf = GeoDataFrame(data, crs='epsg:4326')
        set_geometry(gdf, 'geom_coverage', inplace=True)
        return gdf


_REPO = GeographyRepository()

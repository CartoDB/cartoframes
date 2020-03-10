from pandas import DataFrame
from geopandas import GeoDataFrame

from .....utils.geom_utils import set_geometry
from ..subscriptions import get_subscription_ids
from .constants import COUNTRY_FILTER, CATEGORY_FILTER, PROVIDER_FILTER
from .entity_repo import EntityRepository

GEOGRAPHY_TYPE = 'geography'

_GEOGRAPHY_ID_FIELD = 'id'
_GEOGRAPHY_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [COUNTRY_FILTER, CATEGORY_FILTER, PROVIDER_FILTER]


def get_geography_repo():
    return _REPO


class GeographyRepository(EntityRepository):

    def __init__(self):
        super(GeographyRepository, self).__init__(_GEOGRAPHY_ID_FIELD, _ALLOWED_FILTERS, _GEOGRAPHY_SLUG_FIELD)

    def get_all(self, filters=None, credentials=None):
        if credentials is not None:
            ids = get_subscription_ids(credentials, GEOGRAPHY_TYPE)
            if len(ids) == 0:
                return []
            elif len(ids) > 0:
                filters = filters or {}
                filters['id'] = ids

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
            'id': self._normalize_field(row, self.id_field),
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'country_id': self._normalize_field(row, 'country_id'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'provider_name': self._normalize_field(row, 'provider_name'),
            'lang': self._normalize_field(row, 'lang'),
            'geom_coverage': self._normalize_field(row, 'geom_coverage'),
            'geom_type': self._normalize_field(row, 'geom_type'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'version': self._normalize_field(row, 'version'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'summary_json': self._normalize_field(row, 'summary_json'),
            'available_in': self._normalize_field(row, 'available_in')
        }

    def get_geographies_gdf(self):
        data = self.client.get_geographies({'get_geoms_coverage': True})
        df = DataFrame(data)
        gdf = GeoDataFrame(df, crs='epsg:4326')

        set_geometry(gdf, col='geom_coverage', inplace=True)
        return gdf


_REPO = GeographyRepository()

from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo

_COUNTRY_ID_FIELD = 'id'


class Country(CatalogEntity):

    id_field = _COUNTRY_ID_FIELD
    entity_repo = get_country_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_by_country(self.id)

    @property
    def geographies(self):
        return get_geography_repo().get_by_country(self.id)

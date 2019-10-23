from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.category_repo import get_category_repo
from .repository.constants import COUNTRY_FILTER


class Country(CatalogEntity):

    entity_repo = get_country_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def geographies(self):
        return get_geography_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def categories(self):
        return get_category_repo().get_all({COUNTRY_FILTER: self.id})

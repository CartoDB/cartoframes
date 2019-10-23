from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.constants import CATEGORY_FILTER
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Category(CatalogEntity):

    entity_repo = get_category_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def geographies(self):
        return get_geography_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

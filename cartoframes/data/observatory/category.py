from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


_CATEGORY_ID_FIELD = 'id'


class Category(CatalogEntity):

    id_field = _CATEGORY_ID_FIELD
    entity_repo = get_category_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_by_category(self.id)

    @property
    def name(self):
        return self.data['name']

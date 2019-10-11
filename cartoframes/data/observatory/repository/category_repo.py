from __future__ import absolute_import

from .constants import COUNTRY_FILTER
from .entity_repo import EntityRepository


_CATEGORY_ID_FIELD = 'id'
_ALLOWED_FILTERS = [COUNTRY_FILTER]


def get_category_repo():
    return _REPO


class CategoryRepository(EntityRepository):

    def __init__(self):
        super(CategoryRepository, self).__init__(_CATEGORY_ID_FIELD, _ALLOWED_FILTERS)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.category import Category
        return Category

    def _get_rows(self, filters=None):
        if filters is not None and COUNTRY_FILTER in filters.keys():
            return self.client.get_categories_joined_datasets(filters)

        return self.client.get_categories(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'name': self._normalize_field(row, 'name')
        }


_REPO = CategoryRepository()

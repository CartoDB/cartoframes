from .constants import COUNTRY_FILTER, PROVIDER_FILTER, PUBLIC_FILTER
from .entity_repo import EntityRepository


_CATEGORY_ID_FIELD = 'id'
_ALLOWED_FILTERS = [COUNTRY_FILTER, PROVIDER_FILTER, PUBLIC_FILTER]


def get_category_repo():
    return _REPO


class CategoryRepository(EntityRepository):

    def __init__(self):
        super(CategoryRepository, self).__init__(_CATEGORY_ID_FIELD, _ALLOWED_FILTERS)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.category import Category
        return Category

    def _get_rows(self, filters=None):
        return self.client.get_categories(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'name': self._normalize_field(row, 'name')
        }


_REPO = CategoryRepository()

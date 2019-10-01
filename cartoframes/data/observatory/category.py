from .entity import SingleEntity, EntitiesList
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


_CATEGORY_ID_FIELD = 'id'


class Category(SingleEntity):

    id_field = _CATEGORY_ID_FIELD
    entity_repo = get_category_repo()

    def datasets(self):
        return get_dataset_repo().get_by_category(self.id)


class Categories(EntitiesList):

    id_field = _CATEGORY_ID_FIELD
    entity_repo = get_category_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Category

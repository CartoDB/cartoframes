from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


def get_categories():
    return [Category(cat) for cat in get_category_repo().get_all()]


class Category(object):

    def __init__(self, metadata):
        self.id = metadata.id
        self.name = metadata.name

    @staticmethod
    def get(category_id):
        metadata = get_category_repo().get_category(category_id)
        return Category(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_category(self.id)

from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


class Category(object):

    def __init__(self, metadata):
        # TODO: Confirm which properties from the DDL we should include here
        self.id = metadata.id
        self.name = metadata.name

    @staticmethod
    def get(category_id):
        metadata = get_category_repo().get_by_id(category_id)
        return Category(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_category(self.id)


class Categories(list):

    def __init__(self, items):
        super(Categories, self).__init__(items)

    @staticmethod
    def get_all():
        return [Category(cat) for cat in get_category_repo().get_all()]

    @staticmethod
    def get(category_id):
        return Category.get(category_id)

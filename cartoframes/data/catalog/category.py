import pandas as pd
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


class Category(pd.Series):

    def __init__(self, category):
        super(Category, self).__init__(category)

    @staticmethod
    def get_by_id(category_id):
        category = get_category_repo().get_by_id(category_id)
        return Category(category)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_category(self.id)


class Categories(pd.DataFrame):

    def __init__(self, items):
        super(Categories, self).__init__(items)

    @staticmethod
    def get_all():
        return Categories([Category(cat) for cat in get_category_repo().get_all()])

    @staticmethod
    def get_by_id(category_id):
        return Category.get_by_id(category_id)

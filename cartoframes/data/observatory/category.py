import pandas as pd

from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo


_CATEGORY_ID_FIELD = 'id'


class Category(pd.Series):

    @property
    def _constructor(self):
        return Category

    @property
    def _constructor_expanddim(self):
        return Categories

    @staticmethod
    def get_by_id(category_id):
        return get_category_repo().by_id(category_id)

    def datasets(self):
        return get_dataset_repo().by_category(self[_CATEGORY_ID_FIELD])

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Categories(pd.DataFrame):

    @property
    def _constructor(self):
        return Categories

    @property
    def _constructor_sliced(self):
        return Category

    @staticmethod
    def all():
        return get_category_repo().all()

    @staticmethod
    def get_by_id(category_id):
        return Category.get_by_id(category_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

import pandas as pd

from cartoframes.data.catalog.dataset import Datasets

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
        category = get_category_repo().get_by_id(category_id)
        return Category(category)

    @property
    def datasets(self):
        return Datasets(get_dataset_repo().get_by_category(self[_CATEGORY_ID_FIELD]))


class Categories(pd.DataFrame):

    @property
    def _constructor(self):
        return Categories

    @property
    def _constructor_sliced(self):
        return Category

    @staticmethod
    def get_all():
        return Categories([Category(cat) for cat in get_category_repo().get_all()])

    @staticmethod
    def get_by_id(category_id):
        return Category.get_by_id(category_id)

import pandas as pd

from cartoframes.exceptions import DiscoveryException
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
        return get_category_repo().get_by_id(category_id)

    def datasets(self):
        return get_dataset_repo().get_by_category(self._get_id())

    def _get_id(self):
        try:
            return self[_CATEGORY_ID_FIELD]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of Categories '
                                     'class. You should use `Categories.get_by_id("category_id")` to obtain a valid '
                                     'instance of the Category class and then attempt this function on it.')

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

    def __init__(self, data):
        super(Categories, self).__init__(data)
        self.set_index(_CATEGORY_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_category_repo().get_all()

    @staticmethod
    def get_by_id(category_id):
        return Category.get_by_id(category_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

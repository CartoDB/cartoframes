from .category import Category
from .country import Country
from .dataset import Dataset


class Catalog(object):

    @property
    def countries(self):
        return Country.get_all()

    @property
    def categories(self):
        return Category.get_all()

    @property
    def datasets(self):
        return Dataset.get_all()

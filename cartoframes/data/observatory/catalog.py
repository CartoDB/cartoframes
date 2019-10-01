from .category import Categories
from .country import Countries
from .dataset import Datasets


class Catalog(object):

    @staticmethod
    def countries():
        return Countries.get_all()

    @staticmethod
    def categories():
        return Categories.get_all()

    @staticmethod
    def datasets():
        return Datasets.get_all()

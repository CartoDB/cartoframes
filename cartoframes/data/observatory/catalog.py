from .category import Categories
from .country import Countries


class Catalog(object):

    @staticmethod
    def countries():
        return Countries.all()

    @staticmethod
    def categories():
        return Categories.all()

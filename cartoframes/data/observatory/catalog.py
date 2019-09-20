from .category import Categories
from .country import Countries


class Catalog(object):

    @staticmethod
    def countries():
        return Countries.get_all()

    @staticmethod
    def categories():
        return Categories.get_all()

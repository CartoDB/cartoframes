from .category import get_categories
from .country import get_countries


class DO(object):

    @staticmethod
    def countries():
        return get_countries()

    @staticmethod
    def categories():
        return get_categories()

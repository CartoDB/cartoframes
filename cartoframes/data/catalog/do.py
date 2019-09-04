from .category import Categories
from .country import Countries


class DO(object):

    def __init__(self):
        self.countries = Countries.get_all()
        self.categories = Categories.get_all()

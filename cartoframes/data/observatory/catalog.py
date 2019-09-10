from cartoframes.data.observatory.category import Categories
from cartoframes.data.observatory.country import Countries


class Catalog(object):

    @property
    def countries(self):
        return Countries.get_all()

    @property
    def categories(self):
        return Categories.get_all()

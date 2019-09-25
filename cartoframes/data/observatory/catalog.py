from __future__ import absolute_import

from .category import Categories
from .country import Countries


class Catalog(object):
    """Data Observatory Catalog"""

    @staticmethod
    def countries():
        """Get all the countries in the Catalog

        Returns:
            :py:class:`Categories <cartoframes.data.observatory.Countries>`

        """

        return Countries.get_all()

    @staticmethod
    def categories():
        """Get all the categories in the Catalog

        Returns:
            :py:class:`Categories <cartoframes.data.observatory.Categories>`

        """

        return Categories.get_all()

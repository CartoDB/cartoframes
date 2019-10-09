from __future__ import absolute_import

from .category import Category
from .country import Country
from .geography import Geography
from .dataset import Dataset
from .repository.constants import COUNTRY_FILTER, CATEGORY_FILTER, GEOGRAPHY_FILTER


class Catalog(object):
    """Data Observatory Catalog"""

    def __init__(self):
        self.filters = {}

    @property
    def countries(self):
        """Get all the countries in the Catalog

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Country.get_all(self.filters)

    @property
    def categories(self):
        """Get all the categories in the Catalog

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Category.get_all(self.filters)

    @property
    def datasets(self):
        """Get all the datasets in the Catalog

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Dataset.get_all(self.filters)

    @property
    def geographies(self):
        """Get all the geographies in the Catalog

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Geography.get_all(self.filters)

    def country(self, country_id):
        self.filters[COUNTRY_FILTER] = country_id
        return self

    def category(self, category_id):
        self.filters[CATEGORY_FILTER] = category_id
        return self

    def geography(self, geography_id):
        self.filters[GEOGRAPHY_FILTER] = geography_id
        return self

    def clear_filters(self):
        self.filters = {}

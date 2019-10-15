from __future__ import absolute_import

from .entity import is_slug_value
from .category import Category
from .country import Country
from .geography import Geography
from .dataset import Dataset
from .subscriptions import Subscriptions
from .repository.constants import COUNTRY_FILTER, CATEGORY_FILTER, GEOGRAPHY_FILTER

from ...auth import Credentials, defaults


class Catalog(object):
    """Data Observatory Catalog"""

    def __init__(self):
        self.filters = {}

    @property
    def countries(self):
        """Get all the countries in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Country.get_all(self.filters)

    @property
    def categories(self):
        """Get all the categories in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Category.get_all(self.filters)

    @property
    def datasets(self):
        """Get all the datasets in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Dataset.get_all(self.filters)

    @property
    def geographies(self):
        """Get all the geographies in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """

        return Geography.get_all(self.filters)

    def country(self, country_id):
        """Add a country filter to the current Catalog instance.

        Args:
            country_id (str):
              Id value of the country to be used for filtering the Catalog.

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.catalog.Catalog>`

        """

        self.filters[COUNTRY_FILTER] = country_id
        return self

    def category(self, category_id):
        """Add a category filter to the current Catalog instance.

        Args:
            category_id (str):
              Id value of the category to be used for filtering the Catalog.

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.catalog.Catalog>`

        """

        self.filters[CATEGORY_FILTER] = category_id
        return self

    def geography(self, geography_id):
        """Add a geography filter to the current Catalog instance.

        Args:
            geography_id (str):
              Id or slug value of the geography to be used for filtering the Catalog

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.catalog.Catalog>`

        """

        filter_value = geography_id

        if is_slug_value(geography_id):
            geography = Geography.get(geography_id)
            filter_value = geography.id

        self.filters[GEOGRAPHY_FILTER] = filter_value
        return self

    def clear_filters(self):
        """Remove the current filters from this Catalog instance."""

        self.filters = {}

    def subscriptions(self, credentials=None):
        """Get all the subscriptions in the Catalog

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            :py:class:`Datasets <cartoframes.data.observatory.Datasets>`

        """

        _no_filters = {}
        _credentials = credentials or defaults.get_default_credentials()

        if not isinstance(_credentials, Credentials):
            raise ValueError('`credentials` must be a Credentials class instance')

        return Subscriptions(
            Dataset.get_all(_no_filters, _credentials),
            Geography.get_all(_no_filters, _credentials)
        )

from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.category_repo import get_category_repo
from .repository.constants import COUNTRY_FILTER


class Country(CatalogEntity):
    """Every CatalogDataset has a country associated to it. A Country instance can be used to query datasets (or other
    entities related to datasets) that belong to that country.
    """

    entity_repo = get_country_repo()

    @property
    def datasets(self):
        """Get the list of datasets covering data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of CatalogDataset instances.

        """
        return get_dataset_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def geographies(self):
        """Get the list of geographies covering data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Geography instances.

        """
        return get_geography_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def categories(self):
        """Get the list of categories that are assigned to datasets that cover data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Category instances.

        """
        return get_category_repo().get_all({COUNTRY_FILTER: self.id})

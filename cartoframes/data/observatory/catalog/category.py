from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.constants import CATEGORY_FILTER
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Category(CatalogEntity):

    """A CatalogDataset can be assigned to a particular categories as part of its metadata info. A Category instance
    can be used to query datasets or geographies that belong (or are related to) that category.
    """

    entity_repo = get_category_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this category.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of CatalogDataset instances.

        """
        return get_dataset_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def geographies(self):
        """Get the list of geographies corresponding to datasets that are related to this category.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """
        return get_geography_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def name(self):
        """Name of this category."""

        return self.data['name']

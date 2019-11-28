from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.provider_repo import get_provider_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.constants import PROVIDER_FILTER


class Provider(CatalogEntity):
    """This class represents a :py:class:`Provider <cartoframes.data.observatory.Provider>`
    of datasets and geographies in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`.

    Examples:
        List the available providers in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`
        in combination with nested filters (categories, countries, etc.)

        .. code::

            from cartoframes.data.observatory import Provider

            providers = Provider.get_all()

        Get a :py:class:`Provider <cartoframes.data.observatory.Provider>` from the
        :py:class:`Catalog <cartoframes.data.observatory.Catalog>` given its ID

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = Catalog()
            provider = catalog.provider('mrli')
    """

    _entity_repo = get_provider_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this provider.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        :raises DiscoveryException: When no datasets are found.
        :raises CartoException: If there's a problem when connecting to the catalog.

        Examples:

            .. code::

                from cartoframes.data.observatory import Catalog

                catalog = Catalog()
                datasets = catalog.provider('mrli').datasets

        """

        return get_dataset_repo().get_all({PROVIDER_FILTER: self.id})

    @property
    def name(self):
        """Name of this provider."""

        return self.data['name']

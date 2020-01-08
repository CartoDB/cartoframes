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

        >>> providers = Provider.get_all()

        Get a :py:class:`Provider <cartoframes.data.observatory.Provider>` from the
        :py:class:`Catalog <cartoframes.data.observatory.Catalog>` given its ID

        >>> catalog = Catalog()
        >>> provider = catalog.provider('mrli')

    """
    _entity_repo = get_provider_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this provider.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        Examples:
            >>> provider = Provider.get('mrli')
            >>> datasets = provider.datasets

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> datasets = catalog.provider('mrli').datasets

        """
        return get_dataset_repo().get_all({PROVIDER_FILTER: self.id})

    @property
    def name(self):
        """Name of this provider."""
        return self.data['name']

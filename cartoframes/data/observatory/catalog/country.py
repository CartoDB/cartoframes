from .entity import CatalogEntity
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.category_repo import get_category_repo
from .repository.constants import COUNTRY_FILTER


class Country(CatalogEntity):
    """This class represents a :py:class:`Country <cartoframes.data.observatory.Country>`
    in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`. Catalog datasets
    (:py:class:`Dataset <cartoframes.data.observatory.Dataset>` class)
    belong to a country, so you can filter available `datasets` and
    `geographies` that belong (or are related) to a given `Country`.

    Examples:
        List the available countries in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

        >>> catalog = Catalog()
        >>> countries = catalog.countries

        Get a :py:class:`Country <cartoframes.data.observatory.Country>` from the
        :py:class:`Catalog <cartoframes.data.observatory.Catalog>` given its ID

        >>> # country ID is a lowercase ISO Alpha 3 Code
        >>> country = Country.get('usa')

    """
    _entity_repo = get_country_repo()

    @property
    def datasets(self):
        """Get the list of :obj:`Dataset` covering data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        Examples:
            Get all the `datasets` :py:class:`Dataset <cartoframes.data.observatory.Dataset>` available
            in the `catalog` for a :py:class:`Country <cartoframes.data.observatory.Country>` instance

            >>> country = Country.get('usa')
            >>> datasets = country.datasets

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> datasets = catalog.country('usa').datasets

            You can perform these other operations with a
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`:

            >>> datasets = catalog.country('usa').datasets
            >>> # convert the list of datasets into a pandas DataFrame
            >>> # for further filtering and exploration
            >>> dataframe = datasets.to_dataframe()
            >>> # get a dataset by ID or slug
            >>> dataset = Dataset.get(A_VALID_ID_OR_SLUG)

        """
        return get_dataset_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def geographies(self):
        """Get the list of :obj:`Geography` covering data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Geography instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no geographies are found.

        Examples:
            Get all the `geographies` :py:class:`Geography <cartoframes.data.observatory.Geography>` available
            in the `catalog` for a :py:class:`Country <cartoframes.data.observatory.Country>` instance

            >>> country = Country.get('usa')
            >>> geographies = country.geographies

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> geographies = catalog.country('usa').geographies

            You can perform these other operations with a
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`:

            >>> geographies = catalog.country('usa').geographies
            >>> # convert the list of geographies into a pandas DataFrame
            >>> # for further filtering and exploration
            >>> dataframe = geographies.to_dataframe()
            >>> # get a geography by ID or slug
            >>> geography = Geography.get(A_VALID_ID_OR_SLUG)

        """
        return get_geography_repo().get_all({COUNTRY_FILTER: self.id})

    @property
    def categories(self):
        """Get the list of :obj:`Category` that are assigned to :obj:`Dataset` that cover data for this country.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Category instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        Examples:
            Get all the `categories` :py:class:`Category <cartoframes.data.observatory.Category>` available
            in the `catalog` for a :py:class:`Country <cartoframes.data.observatory.Country>` instance

            >>> country = Country.get('usa')
            >>> categories = country.categories

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> category = catalog.country('usa').categories

        """
        return get_category_repo().get_all({COUNTRY_FILTER: self.id})

    def __repr__(self):
        return "<{classname}.get('{entity_id}')> #'{descr}'" \
               .format(classname=self.__class__.__name__, entity_id=self._get_print_id(), descr=self.data['name'])

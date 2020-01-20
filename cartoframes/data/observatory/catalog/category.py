from .entity import CatalogEntity
from .repository.constants import CATEGORY_FILTER
from .repository.category_repo import get_category_repo
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Category(CatalogEntity):
    """This class represents a :py:class:`Category <cartoframes.data.observatory.Category>`
    in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`. Catalog datasets
    (:py:class:`Dataset <cartoframes.data.observatory.Dataset>` class)
    are grouped by `categories`, so you can filter available `datasets` and
    `geographies` that belong (or are related) to a given `Category`.

    Examples:
        List the available categories in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

        >>> catalog = Catalog()
        >>> categories = catalog.categories

        Get a :py:class:`Category <cartoframes.data.observatory.Category>` from the
        :py:class:`Catalog <cartoframes.data.observatory.Catalog>` given its ID

        >>> category = Category.get('demographics')

    """
    _entity_repo = get_category_repo()

    @property
    def datasets(self):
        """Get the list of :obj:`Dataset` related to this category.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        Examples:
            Get all the `datasets` :py:class:`Dataset <cartoframes.data.observatory.Dataset>` available
            in the `catalog` for a :py:class:`Category <cartoframes.data.observatory.Category>` instance

            >>> category = Category.get('demographics')
            >>> datasets = category.datasets

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> datasets = catalog.category('demographics').datasets

            You can perform other operations with a
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`:

            >>> catalog = Catalog()
            >>> datasets = catalog.category('demographics').datasets
            >>> # convert the list of datasets into a pandas DataFrame
            >>> # for further filtering and exploration
            >>> dataframe = datasets.to_dataframe()
            >>> # get a dataset by ID or slug
            >>> dataset = Dataset.get(A_VALID_ID_OR_SLUG)

        """
        return get_dataset_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def geographies(self):
        """Get the list of :obj:`Geography` related to this category.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Geography instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        Examples:
            Get all the `geographies` :py:class:`Dataset <cartoframes.data.observatory.Dataset>` available
            in the `catalog` for a :py:class:`Category <cartoframes.data.observatory.Category>` instance

            >>> category = Category.get('demographics')
            >>> geographies = category.geographies

            Same example as above but using nested filters:

            >>> catalog = Catalog()
            >>> geographies = catalog.category('demographics').geographies

            You can perform these other operations with a
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`:

            >>> catalog = Catalog()
            >>> geographies = catalog.category('demographics').geographies
            >>> # convert the list of datasets into a pandas DataFrame
            >>> # for further filtering and exploration
            >>> dataframe = geographies.to_dataframe()
            >>> # get a geography by ID or slug
            >>> dataset = Geography.get(A_VALID_ID_OR_SLUG)

        """
        return get_geography_repo().get_all({CATEGORY_FILTER: self.id})

    @property
    def name(self):
        """Name of this category instance."""
        return self.data['name']

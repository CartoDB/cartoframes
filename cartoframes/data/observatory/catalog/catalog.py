from .entity import is_slug_value
from .country import Country
from .category import Category
from .provider import Provider
from .dataset import Dataset
from .geography import Geography
from .subscriptions import Subscriptions
from .repository.constants import (COUNTRY_FILTER, CATEGORY_FILTER, GEOGRAPHY_FILTER, GLOBAL_COUNTRY_FILTER,
                                   PROVIDER_FILTER, PUBLIC_FILTER)

from ....utils.logger import log
from ....utils.utils import get_credentials


class Catalog:
    """This class represents the Data Observatory metadata
    :py:class:`Catalog <cartoframes.data.observatory.Catalog>`.

    The catalog contains metadata that helps to discover and understand the
    data available in the Data Observatory for :py:attr:`Dataset.download` and :obj:`Enrichment` purposes.

    You can get more information about the Data Observatory catalog from the
    `CARTO website <https://carto.com/platform/location-data-streams/>`__ and in your CARTO user account dashboard.

    The Catalog has three main purposes:
      - Explore and discover the datasets available in the repository (both public and premium datasets).
      - Subscribe to some premium datasets and manage your datasets licenses.
      - Download data and use your licensed datasets and variables to enrich your own data by means of the
        :obj:`Enrichment` functions.

    The Catalog is public and can be explored without a CARTO account. Once you discover a
    :obj:`Dataset` of interest and want to acquire a license to use it, you'll need a CARTO account to
    subscribe to it, by means of the :py:attr:`Dataset.subscribe` or :py:attr:`Geography.subscribe` functions.

    The Catalog is composed of three main entities:
      - :obj:`Dataset`: It is the main :obj:`CatalogEntity`. It contains metadata of the actual data
        you can use to :py:attr:`Dataset.download` or for :obj:`Enrichment` purposes.
      - :obj:`Geography`: Datasets in the Data Observatory are aggregated by different geographic boundaries.
        The `Geography` entity contains metadata to understand the boundaries of a :obj:`Dataset`. It's used for
        enrichment and you can also :py:attr:`Geography.download` the underlying data.
      - :obj:`Variable`: Variables contain metadata about the columns available in each dataset for enrichment.
        Let's say you explore a `dataset` with demographic data for the whole US at the Census tract level.
        The variables give you information about the actual columns you have available, such as: total_population,
        total_males, etc.
        On the other hand, you can use lists of `Variable` instances, :py:attr:`Variable.id`, or
        :py:attr:`Variable.slug` to enrich your own data.

    Every `Dataset` is related to a `Geography`. You can have for example, demographics data at the Census
    tract, block groups or blocks levels.

    When subscribing to a premium dataset, you should subscribe to both the :py:attr:`Dataset.subscribe` and the
    :py:attr:`Geography.subscribe` to be able to access both tables to enrich your own data.

    The two main entities of the Catalog (`Dataset` and `Geography`) are related to other entities, that
    are useful for a hierarchical categorization and discovery of available data in the Data Observatory:

      - :obj:`Category`: Groups datasets of the same topic, for example, `demographics`, `financial`, etc.
      - :obj:`Country`: Groups datasets available by country
      - :obj:`Provider`: Gives you information about the provider of the source data

    You can just list all the grouping entities. Take into account this is not the preferred way
    to discover the catalog metadata, since there can be thousands of entities on it:

    >>> Category.get_all()
    [<Category.get('demographics')>, ...]
    >>> Country.get_all()
    [<Country.get('usa')>, ...]
    >>> Provider.get_all()
    [<Provider.get('mrli')>, ...]

    Or you can get them by ID:

    >>> Category.get('demographics')
    <Category.get('demographics')>
    >>> Country.get('usa')
    <Country.get('usa')>
    >>> Provider.get('mrli')
    <Provider.get('mrli')>

    Examples:
        The preferred way of discover the available datasets in the Catalog is through nested filters

        >>> catalog = Catalog()
        >>> catalog.country('usa').category('demographics').datasets
        [<Dataset.get('acs_sociodemogr_b758e778')>, ...]

        You can include the geography as part of the nested filter like this:

        >>> catalog = Catalog()
        >>> catalog.country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets

        If a filter is already applied to a Catalog instance and you want to do a new hierarchical search,
        clear the previous filters with the `Catalog().clear_filters()` method:

        >>> catalog = Catalog()
        >>> catalog.country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets
        >>> catalog.clear_filters()
        >>> catalog.country('esp').category('demographics').datasets

        Otherwise the filters accumulate and you'll get unexpected results.

        During the discovery process, it's useful to understand the related metadata to a given Geography or Dataset.
        A useful way of reading or filtering by metadata values consists on converting the entities to a pandas
        DataFrame:

        >>> catalog = Catalog()
        >>> catalog.country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets.to_dataframe()

        For each dataset in the Catalog, you can explore its variables, get a summary of its stats, etc.

        >>> dataset = Dataset.get('od_acs_13345497')
        >>> dataset.variables
        [<Variable.get('dwellings_2_uni_fb8f6cfb')> #'Two-family (two unit) dwellings', ...]

    See the Catalog guides and examples in our
    `public documentation website <https://carto.com/developers/cartoframes/guides/Introduction/>`__
    for more information.

    """
    def __init__(self):
        self.filters = {}

    @property
    def countries(self):
        """Get all the countries with datasets available in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no countries are found.

        """
        return Country.get_all(self.filters)

    @property
    def categories(self):
        """Get all the categories in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no categories are found.

        """
        self._global_message()
        return Category.get_all(self.filters)

    @property
    def providers(self):
        """Get all the providers in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no providers are found.

        """
        self._global_message()
        return Provider.get_all(self.filters)

    @property
    def datasets(self):
        """Get all the datasets in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        """
        self._global_message()
        return Dataset.get_all(self.filters)

    @property
    def geographies(self):
        """Get all the geographies in the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no geographies are found.

        """
        self._global_message()
        return Geography.get_all(self.filters)

    def country(self, country_id):
        """Add a country filter to the current Catalog instance.

        Args:
            country_id (str):
              ID of the country to be used for filtering the Catalog.

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

        """
        self.filters[COUNTRY_FILTER] = country_id
        return self

    def category(self, category_id):
        """Add a category filter to the current Catalog instance.

        Args:
            category_id (str):
              ID of the category to be used for filtering the Catalog.

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

        """
        self.filters[CATEGORY_FILTER] = category_id
        return self

    def geography(self, geography_id):
        """Add a geography filter to the current Catalog instance.

        Args:
            geography_id (str):
              ID or slug of the geography to be used for filtering the Catalog

        Returns:
            :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

        """
        filter_value = geography_id

        if is_slug_value(geography_id):
            geography = Geography.get(geography_id)
            filter_value = geography.id

        self.filters[GEOGRAPHY_FILTER] = filter_value
        return self

    def provider(self, provider_id):
        """Add a provider filter to the current Catalog instance

        Args:
            provider_id (str):
              ID of the provider to be used for filtering the Catalog.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """
        self.filters[PROVIDER_FILTER] = provider_id
        return self

    def public(self, is_public=True):
        """Add a public filter to the current Catalog instance

        Args:
            is_public (str, optional):
              Flag to filter public (True) or private (False) datasets. Default is True.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>`

        """
        self.filters[PUBLIC_FILTER] = 'true' if is_public else 'false'
        return self

    def clear_filters(self):
        """Remove the current filters from this Catalog instance."""
        self.filters = {}

    def subscriptions(self, credentials=None):
        """Get all the subscriptions in the Catalog. You'll get all the `Dataset` or `Geography` instances you have
        previously subscribed to.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            :py:class:`Subscriptions <cartoframes.data.observatory.Subscriptions>`

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        """
        _credentials = get_credentials(credentials)

        return Subscriptions(_credentials)

    def datasets_filter(self, filter_dataset):
        """Get all the datasets in the Catalog filtered
        Returns:
            :py:class:`Dataset <cartoframes.data.observatory.Dataset>`

        """
        return Dataset.get_datasets_spatial_filtered(filter_dataset)

    def _global_message(self):
        if self.filters and self.filters.get(COUNTRY_FILTER) != GLOBAL_COUNTRY_FILTER:
            log.info('You can find more entities with the Global country filter. To apply that filter run:'
                     "\n\tCatalog().country('glo')")

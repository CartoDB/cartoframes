from __future__ import absolute_import

from carto.exceptions import CartoException

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo
from .repository.constants import GEOGRAPHY_FILTER
from . import subscription_info
from . import subscriptions
from . import utils
from ....auth import Credentials, defaults

GEOGRAPHY_TYPE = 'geography'


class Geography(CatalogEntity):
    """A Geography represents the metadata of a particular geography dataset in the catalog.

    If you have Data Observatory enabled in your CARTO account you can:

      - Use any public geography to enrich your data with the variables in it by means of the :obj:`Enrichment`
        functions.
      - Subscribe (:py:attr:`Geography.subscribe`) to any premium geography, to get a license, that grants you
        the right to enrich your data with the variables in it.

    See the enrichment guides for more information about geographies, variables and
    enrichment functions.

    The metadata of a geography allows you to understand the underlying data,
    from variables (the actual columns in the geography, data types, etc.), to a
    description of the provider, source, country, geography available, etc.

    See the attributes reference in this class to understand the metadata available
    for each geography in the catalog.

    Examples:
        There are many different ways to explore the available geographies in the
        catalog.

        You can just list all the available geographies:

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = Catalog()
            geographies = catalog.geographies

        Since the catalog contains thousands of geographies, you can convert the
        list of `geographies` to a pandas DataFrame for further filtering:

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = Catalog()
            dataframe = catalog.geographies.to_dataframe()

        The catalog supports nested filters for a hierarchical exploration.
        This way you could list the geographies available for different hierarchies:
        country, provider, category or a combination of them.

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = Catalog()
            catalog.country('usa').category('demographics').geographies

        Usually you use a geography ID as an intermediate filter to get a list
        of datasets with aggregate data for that geographical resolution

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = Catalog()
            catalog.country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets
    """

    _entity_repo = get_geography_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this geography.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        :raises DiscoveryException: When no datasets are found.
        :raises CartoException: If there's a problem when connecting to the catalog.
        """
        return get_dataset_repo().get_all({GEOGRAPHY_FILTER: self.id})

    @property
    def name(self):
        """Name of this geography."""

        return self.data['name']

    @property
    def description(self):
        """Description of this geography."""

        return self.data['description']

    @property
    def country(self):
        """Code (ISO 3166-1 alpha-3) of the country of this geography."""

        return self.data['country_id']

    @property
    def language(self):
        """Code (ISO 639-3) of the language that corresponds to the data of this geography. """

        return self.data['lang']

    @property
    def provider(self):
        """Id of the Provider of this geography."""

        return self.data['provider_id']

    @property
    def provider_name(self):
        """Name of the Provider of this geography."""
        return self.data['provider_name']

    @property
    def geom_coverage(self):
        """Shows a map to visualize the geographical coverage of the geography data.
        """

        return self.data['geom_coverage']

    @property
    def geom_type(self):
        """Info about the type of geometry of this geography."""

        return self.data['geom_type']

    @property
    def update_frequency(self):
        """Frequency in which the geography data is updated.

        Example: monthly, yearly, etc.
        """

        return self.data['update_frequency']

    @property
    def version(self):
        """Internal version info of this geography."""

        return self.data['version']

    @property
    def is_public_data(self):
        """Allows to check if the content of this geography can be accessed
        with public credentials or if it is a premium geography that needs
        a subscription.

        Returns:
            A boolean value:
                * ``True`` if the geography is public
                * ``False`` if the geography is premium
                    (it requires to :py:attr:`Geography.subscribe`)
        """

        return self.data['is_public_data']

    @property
    def summary(self):
        """dict with extra metadata that summarizes different properties of the geography content."""

        return self.data['summary_json']

    @classmethod
    def get_all(cls, filters=None, credentials=None):
        """Get all the Geography instances that comply with the indicated filters (or all of them if no filters
        are passed. If credentials are given, only the geographies granted for those credentials are returned.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If provided, only geographies granted for those credentials are
                returned.

            filters (dict, optional):
                Dict containing pairs of geography properties and its value to be used as filters to query the available
                geographies. If none is provided, no filters will be applied to the query.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Geography instances.

        :raises DiscoveryException: When no geographies are found.
        :raises CartoException: If there's a problem when connecting to the catalog.
        """

        return cls._entity_repo.get_all(filters, credentials)

    def download(self, credentials=None):
        """Download Geography data as a pandas DataFrame locally. You need Data Observatory enabled in your CARTO
        account, please contact us at support@carto.com for more information.

        For premium geographies (those with `is_public_data` set to False), you need a subscription to the geography.
        Check the subscription guides for more information.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            A string with the local file path with the file downloaded

        :raises CartoException: If you have not a valid license for the dataset being downloaded.
        :raises ValueError: If the credentials argument is not valud.
        """
        if not self._is_subscribed(credentials):
            raise CartoException('You are not subscribed to this Geography yet. Please, use the subscribe method '
                                 'first.')

        return self._download(credentials)

    def subscribe(self, credentials=None):
        """Subscribe to a Geography. You need Data Observatory enabled in your CARTO account, please contact us at
        support@carto.com for more information.

        Geographies with `is_public_data` set to True, do not need a license (i.e. a subscription) to be used.
        Geographies with `is_public_data` set to False, do need a license (i.e. a subscription) to be used. You'll get a
        license to use this `geography` depending on the `estimated_delivery_days` set for this specific geography.

        See :py:meth:`subscription_info <cartoframes.data.observatory.Geography.subscription_info>` for more
        info

        Once you :py:attr:`Geography.subscribe` to a geography you can :py:attr:`Geography.download` its data and
        use the enrichment functions. See the enrichment guides for more info.

        You can check the status of your subscriptions by calling the
        :py:meth:`subscriptions <cartoframes.data.observatory.Catalog.subscriptions>` method in the :obj:`Catalog` with
        your CARTO credentials.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        :raises CartoException: If there's a problem when connecting to the catalog.
        """

        _credentials = self._get_credentials(credentials)
        _subscribed_ids = subscriptions.get_subscription_ids(_credentials)

        if self.id in _subscribed_ids:
            utils.display_existing_subscription_message(self.id, GEOGRAPHY_TYPE)
        else:
            utils.display_subscription_form(self.id, GEOGRAPHY_TYPE, _credentials)

    def subscription_info(self, credentials=None):
        """Get the subscription information of a Geography, which includes the license, TOS, rights, prize and
        estimated_time_of_delivery, among other metadata of interest during the subscription process.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            :py:class:`SubscriptionInfo <cartoframes.data.observatory.SubscriptionInfo>` SubscriptionInfo instance.

        :raises CartoException: If there's a problem when connecting to the catalog.
        """

        _credentials = self._get_credentials(credentials)

        return subscription_info.SubscriptionInfo(
            subscription_info.fetch_subscription_info(self.id, GEOGRAPHY_TYPE, _credentials))

    def _is_subscribed(self, credentials=None):
        if self.is_public_data:
            return True

        _credentials = credentials or defaults.get_default_credentials()

        if not isinstance(_credentials, Credentials):
            raise ValueError('`credentials` must be a Credentials class instance')

        geographies = Geography.get_all({}, _credentials)

        return self in geographies

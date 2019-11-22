from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo
from .repository.constants import GEOGRAPHY_FILTER
from . import subscription_info
from . import subscriptions
from . import utils

GEOGRAPHY_TYPE = 'geography'


class Geography(CatalogEntity):

    entity_repo = get_geography_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this geography.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

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
        return self.data['provider_name']

    @property
    def geom_coverage(self):
        """Info about the geometric coverage of this geography."""

        return self.data['geom_coverage']

    @property
    def update_frequency(self):
        """Frequency in which the geography is updated."""

        return self.data['update_frequency']

    @property
    def version(self):
        """Version info of this geography."""

        return self.data['version']

    @property
    def is_public_data(self):
        """True if the content of this geography can be accessed with public credentials. False otherwise."""

        return self.data['is_public_data']

    @property
    def summary(self):
        """JSON object with extra metadata that summarizes different properties of the dataset content."""

        return self.data['summary_json']

    @classmethod
    def get_all(cls, filters=None, credentials=None):
        """Get all the Geography instances that comply with the indicated filters (or all of them if no filters
        are passed. If credentials are given, only the geographies granted for those credentials are returned.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If provided, only datasets granted for those credentials are
                returned.

            filters (dict, optional):
                Dict containing pairs of geography properties and its value to be used as filters to query the available
                geographies. If none is provided, no filters will be applied to the query.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Geography instances.

        """

        return cls.entity_repo.get_all(filters, credentials)

    def download(self, credentials=None):
        """Download Geography data.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        return self._download(credentials)

    def subscribe(self, credentials=None):
        """Subscribe to a Geography.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)
        _subscribed_ids = subscriptions.get_subscription_ids(_credentials)

        if self.id in _subscribed_ids:
            utils.display_existing_subscription_message(self.id, GEOGRAPHY_TYPE)
        else:
            utils.display_subscription_form(self.id, GEOGRAPHY_TYPE, _credentials)

    def subscription_info(self, credentials=None):
        """Get the subscription information of a Geography.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)

        return subscription_info.SubscriptionInfo(
            subscription_info.fetch_subscription_info(self.id, GEOGRAPHY_TYPE, _credentials))

    def is_available_in(self, platform='bq'):
        return self._is_available_in(platform)

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
        return get_dataset_repo().get_all({GEOGRAPHY_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def country(self):
        return self.data['country_id']

    @property
    def language(self):
        return self.data['lang']

    @property
    def provider(self):
        return self.data['provider_id']

    @property
    def geom_coverage(self):
        return self.data['geom_coverage']

    @property
    def update_frequency(self):
        return self.data['update_frequency']

    @property
    def version(self):
        return self.data['version']

    @property
    def is_public_data(self):
        return self.data['is_public_data']

    @property
    def summary(self):
        return self.data['summary_json']

    @classmethod
    def get_all(cls, filters=None, credentials=None):
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

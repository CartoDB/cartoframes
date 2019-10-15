from __future__ import absolute_import


from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo
from .repository.constants import DATASET_FILTER
from . import subscription_info
from . import subscriptions
from . import utils

DATASET_TYPE = 'dataset'


class Dataset(CatalogEntity):
    entity_repo = get_dataset_repo()

    @property
    def variables(self):
        return get_variable_repo().get_all({DATASET_FILTER: self.id})

    @property
    def variables_groups(self):
        return get_variable_group_repo().get_all({DATASET_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def provider(self):
        return self.data['provider_id']

    @property
    def category(self):
        return self.data['category_id']

    @property
    def data_source(self):
        return self.data['data_source_id']

    @property
    def country(self):
        return self.data['country_id']

    @property
    def language(self):
        return self.data['lang']

    @property
    def geography(self):
        return self.data['geography_id']

    @property
    def temporal_aggregation(self):
        return self.data['temporal_aggregation']

    @property
    def time_coverage(self):
        return self.data['time_coverage']

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
        return self.data['summary_jsonb']

    @classmethod
    def get_all(cls, filters=None, credentials=None):
        return cls.entity_repo.get_all(filters, credentials)

    def download(self, credentials=None):
        """Download Dataset data.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        return self._download(credentials)

    def subscribe(self, credentials=None):
        """Subscribe to a Dataset.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)
        _subscribed_ids = subscriptions.get_subscription_ids(_credentials)

        if self.id in _subscribed_ids:
            utils.display_existing_subscription_message(self.id, DATASET_TYPE)
        else:
            utils.display_subscription_form(self.id, DATASET_TYPE, _credentials)

    def subscription_info(self, credentials=None):
        """Get the subscription information of a Dataset.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)

        return subscription_info.SubscriptionInfo(
            subscription_info.fetch_subscription_info(self.id, DATASET_TYPE, _credentials))

from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Geography(CatalogEntity):

    entity_repo = get_geography_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_by_geography(self.id)

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def country(self):
        return self.data['country_iso_code3']

    @property
    def language(self):
        return self.data['language_iso_code3']

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
        return self.data['summary_jsonb']

    def download(self, credentials=None):
        return self._download(credentials)

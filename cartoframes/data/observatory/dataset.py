from __future__ import absolute_import

from warnings import warn

from google.api_core.exceptions import NotFound

from carto.exceptions import CartoException

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo
from ..clients.bigquery_client import BigQueryClient
from ...auth import get_default_credentials

_WORKING_PROJECT = 'carto-do-customers'


class Dataset(CatalogEntity):

    entity_repo = get_dataset_repo()

    @property
    def variables(self):
        return get_variable_repo().get_by_dataset(self.id)

    @property
    def variables_groups(self):
        return get_variable_group_repo().get_by_dataset(self.id)

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
        return self.data['country_iso_code3']

    @property
    def language(self):
        return self.data['language_iso_code3']

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

    def download(self, credentials=None):
        credentials = _get_credentials(credentials)
        user_dataset = credentials.username.replace('-', '_')
        bq_client = _get_bigquery_client(_WORKING_PROJECT, credentials)

        project, dataset, table = self.id.split('.')
        view = 'view_{}_{}'.format(dataset.replace('-', '_'), table)

        try:
            file_path = bq_client.download_to_file(_WORKING_PROJECT, user_dataset, view)
        except NotFound:
            raise CartoException('You have not purchased the dataset `{}` yet'.format(self.id))

        warn('Data saved: {}.'.format(file_path))
        warn("Read it by: `pandas.read_csv('{}')`.".format(file_path))

        return file_path


def _get_credentials(credentials=None):
    return credentials or get_default_credentials()


def _get_bigquery_client(project, credentials):
    return BigQueryClient(project, credentials)

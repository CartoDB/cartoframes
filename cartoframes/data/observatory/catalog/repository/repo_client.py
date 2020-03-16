import os

from carto.do_dataset import DODataset

from .....auth import Credentials, defaults

DEFAULT_USER = 'do-metadata'


class RepoClient:

    def __init__(self):
        self._do_dataset = None
        default_credentials = defaults.get_default_credentials() or Credentials(DEFAULT_USER)
        default_auth_client = default_credentials.get_api_key_auth_client()
        self._default_do_dataset = DODataset(auth_client=default_auth_client)

    def set_user_credentials(self, credentials):
        if credentials is not None:
            auth_client = credentials.get_api_key_auth_client()
            self._do_dataset = DODataset(auth_client=auth_client)
        else:
            self._do_dataset = None

    def reset_user_credentials(self):
        self._do_dataset = None

    def get_countries(self, filters=None):
        return self._get_entity('countries', filters)

    def get_categories(self, filters=None):
        return self._get_entity('categories', filters)

    def get_providers(self, filters=None):
        return self._get_entity('providers', filters)

    def get_datasets(self, filters=None):
        return self._get_entity('datasets', filters, use_slug=True)

    def get_geographies(self, filters=None):
        return self._get_entity('geographies', filters, use_slug=True)

    def get_variables(self, filters=None):
        filter_id = self._get_filter_id(filters, use_slug=True)
        if filter_id:
            return self._fetch_entity_id('variables', filter_id)
        else:
            entity = 'datasets/{}/variables'.format(filters.pop('dataset'))
            return self._fetch_entity(entity, filters)

    def get_variables_groups(self, filters=None):
        filter_id = self._get_filter_id(filters, use_slug=True)
        if filter_id:
            return self._fetch_entity_id('variables_groups', filter_id)
        else:
            entity = 'datasets/{0}/variables_groups'.format(filters.pop('dataset'))
            return self._fetch_entity(entity, filters)

    def _get_filter_id(self, filters, use_slug=False):
        if isinstance(filters, dict):
            filter_id = filters.get('id')
            if not filter_id and use_slug:
                filter_id = filters.get('slug')
            return filter_id

    def _get_entity(self, entity, filters=None, use_slug=False):
        filter_id = self._get_filter_id(filters, use_slug)
        if filter_id:
            return self._fetch_entity_id(entity, filter_id)
        else:
            return self._fetch_entity(entity, filters)

    def _fetch_entity_id(self, entity, filter_id):
        if isinstance(filter_id, list):
            return list(filter(None, [self._fetch_entity(os.path.join(entity, _id)) for _id in filter_id]))
        else:
            return self._fetch_entity(os.path.join(entity, filter_id))

    def _fetch_entity(self, entity, filters=None):
        if self._do_dataset:
            return self._do_dataset.metadata(entity, filters)
        else:
            return self._default_do_dataset.metadata(entity, filters)

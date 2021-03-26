from carto.do_dataset import DODataset

from .....auth import Credentials, defaults

DEFAULT_USER = 'do-metadata'


class RepoClient:

    def __init__(self):
        default_credentials = Credentials(DEFAULT_USER)
        default_auth_client = default_credentials.get_api_key_auth_client()
        self._default_do_dataset = DODataset(auth_client=default_auth_client)
        self._user_do_dataset = None
        self._external_do_dataset = None

    def set_user_credentials(self, credentials):
        if credentials is not None:
            auth_client = credentials.get_api_key_auth_client()
            self._user_do_dataset = DODataset(auth_client=auth_client)
        else:
            self._user_do_dataset = None

    def reset_user_credentials(self):
        self._user_do_dataset = None

    def set_external_credentials(self):
        # This must be checked every time to allow the definition of
        # "default_do_credentials" at any point in the code because
        # every repo uses a singleton instance of this client
        external_credentials = defaults.get_default_do_credentials()
        if external_credentials is not None:
            external_auth_client = external_credentials.get_api_key_auth_client()
            self._external_do_dataset = DODataset(auth_client=external_auth_client)
        else:
            self._external_do_dataset = None

    def get_countries(self, filters=None):
        self.set_external_credentials()
        return self._get_entity('countries', filters)

    def get_categories(self, filters=None):
        self.set_external_credentials()
        return self._get_entity('categories', filters)

    def get_providers(self, filters=None):
        self.set_external_credentials()
        return self._get_entity('providers', filters)

    def get_datasets(self, filters=None):
        self.set_external_credentials()
        return self._get_entity('datasets', filters, use_slug=True)

    def get_geographies(self, filters=None):
        self.set_external_credentials()
        return self._get_entity('geographies', filters, use_slug=True)

    def get_variables(self, filters=None):
        self.set_external_credentials()
        filter_id = self._get_filter_id(filters, use_slug=True)
        if filter_id:
            return self._fetch_entity_id('variables', filter_id)
        else:
            entity = 'datasets/{}/variables'.format(filters.pop('dataset'))
            return self._fetch_entity(entity, filters)

    def get_variables_groups(self, filters=None):
        self.set_external_credentials()
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
            return list(filter(None, [self._fetch_entity('{0}/{1}'.format(entity, _id)) for _id in filter_id]))
        else:
            return self._fetch_entity('{0}/{1}'.format(entity, filter_id))

    def _fetch_entity(self, entity, filters=None):
        do_dataset = self._user_do_dataset or self._external_do_dataset or self._default_do_dataset
        return do_dataset.metadata(entity, filters)

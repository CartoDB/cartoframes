import os
import requests
from urllib.parse import urlsplit, urlunsplit, SplitResult
from .....auth import Credentials, get_default_credentials

DEFAULT_USER = 'do-metadata'
API_BASE_PATH = 'api/v4/data/observatory'
REQUEST_VERIFY_SSL = True


class RepoClient:

    __instance = None

    def __init__(self):
        self._user_credentials = None

    def set_user_credentials(self, credentials):
        self._user_credentials = credentials

    def get_countries(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/countries'
        id_filter = filters.get('id')
        if id_filter:
            return self._get_entities_by_id(api_path, id_filter)
        else:
            return self._make_request(api_path, filters)

    def get_categories(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/categories'
        id_filter = filters.get('id')
        if id_filter:
            return self._get_entities_by_id(api_path, id_filter)
        else:
            return self._make_request(api_path, filters)

    def get_providers(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/providers'
        provider_id = filters.get('id')
        if provider_id:
            return self._get_entities_by_id(api_path, provider_id)
        else:
            return self._make_request(api_path, filters)

    def get_variables(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/variables'
        id_filter = filters.get('id') or filters.get('slug')
        if id_filter:
            return self._get_entities_by_id(api_path, id_filter)
        else:
            dataset_id = filters.get('dataset')  # Mandatory filter
            api_path = 'metadata/datasets/{}/variables'.format(dataset_id)
            return self._make_request(api_path, filters)

    def get_variables_groups(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/variables_groups'
        id_filter = filters.get('id') or filters.get('slug')
        if id_filter:
            api_path = 'metadata/variables_groups'
            return self._get_entities_by_id(api_path, id_filter)
        else:
            dataset_id = filters.get('dataset')  # Mandatory filter
            api_path = 'metadata/datasets/{}/variables_groups'.format(dataset_id)
            return self._make_request(api_path, filters)

    def get_geographies(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/geographies'
        id_filter = filters.get('id') or filters.get('slug')
        if id_filter:
            return self._get_entities_by_id(api_path, id_filter)
        else:
            return self._make_request(api_path, filters)

    def get_datasets(self, filters=None):
        filters = filters or {}
        api_path = 'metadata/datasets'
        id_filter = filters.get('id') or filters.get('slug')
        if id_filter:
            return self._get_entities_by_id(api_path, id_filter)
        else:
            return self._make_request(api_path, filters)

    def _get_entities_by_id(self, api_base_path, ids):
        # ids can be an ID or a list of them
        entities = []
        entity_ids = ids if isinstance(ids, list) else [ids]

        for entity_id in entity_ids:
            api_path = os.path.join(api_base_path, entity_id)
            entity = self._make_request(api_path)
            if entity is not None:
                entities.append(entity)

        return entities

    def _make_request(self, api_path, filters=None):
        request_url = self._build_url(api_path, filters)
        req = requests.get(request_url, verify=REQUEST_VERIFY_SSL)
        return req.json()

    def _build_url(self, api_path, filters):
        credentials = self._get_user_credentials()
        filters = filters or {}

        url_params = ['api_key={}'.format(credentials.api_key)]
        for key, value in filters.items():
            url_params.append('{}={}'.format(key, value))

        url = urlsplit(credentials.base_url)

        path = os.path.join(url.path, API_BASE_PATH, api_path)
        query = '&'.join(url_params)

        return urlunsplit(SplitResult(
            scheme=url.scheme, netloc=url.netloc, path=path, query=query, fragment=url.fragment
        ))

    def _get_user_credentials(self):
        return self._user_credentials or get_default_credentials() or Credentials(DEFAULT_USER)

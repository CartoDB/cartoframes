from __future__ import absolute_import

from carto.do_datasets import DODatasetManager

from cartoframes.data.clients import SQLClient
from cartoframes.auth import Credentials


class RepoClient(object):

    __instance = None

    def __init__(self):
        self._user_credentials = None
        self._do_credentials = Credentials('do-metadata', 'default_public')
        self.client = SQLClient(self._do_credentials)

    def set_user_credentials(self, credentials):
        self._user_credentials = credentials

    def get_countries(self, field=None, value=None):
        query = 'SELECT DISTICT country_iso_code3 AS id FROM datasets_public'
        return self._run_query(query, field, value)

    def get_categories(self, field=None, value=None):
        query = 'SELECT * FROM categories_public'
        return self._run_query(query, field, value)

    def get_providers(self, field=None, value=None):
        query = 'SELECT * FROM providers_public'
        return self._run_query(query, field, value)

    def get_variables(self, field=None, value=None):
        query = 'SELECT * FROM variables_public'
        return self._run_query(query, field, value)

    def get_variables_groups(self, field=None, value=None):
        query = 'SELECT * FROM variables_groups_public'
        return self._run_query(query, field, value)

    def get_geographies(self, field=None, value=None):
        query = 'SELECT * FROM geographies_public'
        # TODO future: Filter by purchased geography ids
        return self._run_query(query, field, value)

    def get_datasets(self, field=None, value=None):
        query = 'SELECT * FROM datasets_public'

        extra_condition = ''
        if self._user_credentials is not None:
            extra_condition = 'id IN ({})'.format(self._get_purchased_dataset_ids())

        return self._run_query(query, field, value, extra_condition)

    def _run_query(self, query, field, value, extra_condition=None):
        conditions = self._compute_conditions(field, value, extra_condition)
        if len(conditions) > 0:
            query += ' WHERE {}'.format(' AND '.join(conditions))
        return self.client.query(query)

    def _compute_conditions(self, field, value, extra_condition):
        conditions = []
        if field is not None and value is not None:
            conditions.append("{f} = '{v}'".format(f=field, v=value))
        if extra_condition:
            conditions.append(extra_condition)
        return conditions

    def _get_purchased_dataset_ids(self):
        purchased_datasets = self._fetch_purchased_datasets()
        purchased_dataset_ids = list(map(lambda pd: pd.id, purchased_datasets))
        return ','.join(["'" + id + "'" for id in purchased_dataset_ids])

    def _fetch_purchased_datasets(self):
        api_key_auth_client = self._user_credentials.get_api_key_auth_client()
        do_manager = DODatasetManager(api_key_auth_client)
        if do_manager is not None:
            return do_manager.all()
        return []

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance

from __future__ import absolute_import

from cartoframes.data.clients import SQLClient
from cartoframes.auth import Credentials


class RepoClient(object):

    __instance = None

    def __init__(self):
        self.client = SQLClient(Credentials('do-metadata', 'default_public'))

    def get_countries(self, filters=None):
        query = 'select distinct country_iso_code3 as id from datasets_public'
        return self._run_query(query, filters)

    def get_categories(self, filters=None):
        query = 'select * from categories_public'
        return self._run_query(query, filters)

    def get_providers(self, filters=None):
        query = 'select * from providers_public'
        return self._run_query(query, filters)

    def get_variables(self, filters=None):
        query = 'select * from variables_public'
        return self._run_query(query, filters)

    def get_variables_groups(self, filters=None):
        query = 'select * from variables_groups_public'
        return self._run_query(query, filters)

    def get_geographies(self, filters=None):
        query = 'select * from geographies_public'
        return self._run_query(query, filters)

    def get_datasets(self, filters=None):
        query = 'select * from datasets_public'
        return self._run_query(query, filters)

    def _run_query(self, query, filters):
        if filters is not None and len(filters) > 0:
            conditions = ' and '.join("{} = '{}'".format(key, value) for key, value in filters.items())
            query += " where {}".format(conditions)

        return self.client.query(query)

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance

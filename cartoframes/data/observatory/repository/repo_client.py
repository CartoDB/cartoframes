from __future__ import absolute_import

from cartoframes.data.clients import SQLClient
from cartoframes.auth import Credentials


class RepoClient(object):

    __instance = None

    def __init__(self):
        self.client = SQLClient(Credentials('do-metadata', 'default_public'))

    def get_countries(self, filters=None):
        query = 'select distinct country_id as id from datasets_public'
        return self._run_query(query, filters)

    def get_categories(self, filters=None):
        query = 'select * from categories_public'
        return self._run_query(query, filters)

    def get_categories_joined_datasets(self, filters=None):
        query = 'select distinct c.* from categories_public c, datasets_public d'
        return self._run_join_query(query, "c.id = d.category_id",  filters)

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

    def get_geographies_joined_datasets(self, filters=None):
        query = 'select distinct g.* from geographies_public g, datasets_public d'
        return self._run_join_query(query, "g.id = d.geography_id",  filters)

    def get_datasets(self, filters=None):
        query = 'select * from datasets_public'
        return self._run_query(query, filters)

    def _run_query(self, query, filters):
        if filters is not None and len(filters) > 0:
            conditions = ' and '.join("{} = '{}'".format(key, value) for key, value in filters.items())
            query += " where {}".format(conditions)

        return self.client.query(query)

    def _run_join_query(self, query, join_condition, filters):
        query += " where {}".format(join_condition)

        if filters is not None and len(filters) > 0:
            conditions = ' and '.join("d.{} = '{}'".format(key, value) for key, value in filters.items())
            query += " and {}".format(conditions)

        return self.client.query(query)

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance

from __future__ import absolute_import

from cartoframes.auth import Credentials
from cartoframes.data.clients import SQLClient


class RepoClient(object):

    __instance = None

    def __init__(self):
        self.client = SQLClient(Credentials('do-metadata', 'default_public'))

    def get_countries(self, field=None, value=None):
        query = 'select distinct country_iso_code3 as id from datasets_public'
        return self._run_query(query, field, value)

    def get_categories(self, field=None, value=None):
        query = 'select * from categories_public'
        return self._run_query(query, field, value)

    def get_providers(self, field=None, value=None):
        query = 'select * from providers_public'
        return self._run_query(query, field, value)

    def get_variables(self, field=None, value=None):
        query = 'select * from variables_public'
        return self._run_query(query, field, value)

    def get_variables_groups(self, field=None, value=None):
        query = 'select * from variables_groups_public'
        return self._run_query(query, field, value)

    def get_geographies(self, field=None, value=None):
        query = 'select * from geographies_public'
        return self._run_query(query, field, value)

    def get_datasets(self, field=None, value=None):
        query = 'select * from datasets_public'
        return self._run_query(query, field, value)

    def _run_query(self, query, field, value):
        if field is not None and value is not None:
            query += " where {f} = '{v}'".format(f=field, v=value)

        return self.client.query(query)

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance

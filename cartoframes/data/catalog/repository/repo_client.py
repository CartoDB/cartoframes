from cartoframes.client import SQLClient
from cartoframes.auth import Credentials


class RepoClient(object):

    # __instance = None

    def __init__(self):
        self.client = SQLClient(Credentials('do-metadata', 'default_public'))

    def get_countries(self, field=None, value=None):
        query = 'select distinct country_iso_code3 from datasets'
        return self._run_query(query, field, value)

    def get_categories(self, field=None, value=None):
        query = 'select * from categories'
        return self._run_query(query, field, value)

    def get_variables(self, field=None, value=None):
        query = 'select * from variables'
        return self._run_query(query, field, value)

    def get_datasets(self, field=None, value=None):
        query = 'select * from datasets'
        return self._run_query(query, field, value)

    def _run_query(self, query, field, value):
        if field is not None and value is not None:
            query += " where {f} = '{v}'".format(f=field, v=value)

        return self.client.query(query)

    # def __new__(cls):
    #     if RepoClient.__instance is None:
    #         RepoClient.instance = object.__new__(cls)
    #     return RepoClient.__instance

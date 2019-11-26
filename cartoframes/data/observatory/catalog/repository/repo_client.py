from __future__ import absolute_import

from ..subscriptions import get_subscription_ids
from .....auth import Credentials
from .....core.managers.context_manager import ContextManager


class RepoClient(object):

    __instance = None

    def __init__(self):
        self._user_credentials = None
        self._do_credentials = Credentials('do-metadata', 'default_public')
        self._context_manager = ContextManager(self._do_credentials)

    def set_user_credentials(self, credentials):
        self._user_credentials = credentials

    def get_countries(self, filters=None):
        query = 'SELECT DISTINCT t.country_id AS id FROM datasets_public t'
        return self._run_query(query, filters)

    def get_categories(self, filters=None):
        query = 'SELECT t.* FROM categories_public t'
        return self._run_query(query, filters)

    def get_categories_joined_datasets(self, filters=None):
        query = 'SELECT DISTINCT c.* FROM categories_public c, datasets_public t'
        return self._run_query(query, filters, ['c.id = t.category_id'])

    def get_providers(self, filters=None):
        query = 'SELECT t.* FROM providers_public t'
        return self._run_query(query, filters)

    def get_variables(self, filters=None):
        query = 'SELECT t.* FROM variables_public t'
        return self._run_query(query, filters)

    def get_variables_groups(self, filters=None):
        query = 'SELECT t.* FROM variables_groups_public t'
        return self._run_query(query, filters)

    def get_geographies(self, filters=None):
        query = 'SELECT t.* FROM geographies_public t'

        extra_condition = []
        if self._user_credentials is not None:
            ids = get_subscription_ids(self._user_credentials)
            if len(ids) == 0:
                return []
            elif len(ids) > 0:
                extra_condition.append('t.id IN ({})'.format(ids))

        return self._run_query(query, filters, extra_condition)

    def get_geographies_joined_datasets(self, filters=None):
        query = 'SELECT DISTINCT g.* FROM geographies_public g, datasets_public t'
        return self._run_query(query, filters, ['g.id = t.geography_id'])

    def get_datasets(self, filters=None):
        query = 'SELECT t.* FROM datasets_public t'

        extra_condition = []
        if self._user_credentials is not None:
            ids = get_subscription_ids(self._user_credentials)
            if len(ids) == 0:
                return []
            elif len(ids) > 0:
                extra_condition.append('t.id IN ({})'.format(ids))

        return self._run_query(query, filters, extra_condition)

    def _run_query(self, query, filters, extra_conditions=None):
        conditions = self._compute_conditions(filters, extra_conditions)

        if len(conditions) > 0:
            where_clause = ' AND '.join(conditions)
            query += ' WHERE {}'.format(where_clause)

        return self._context_manager.execute_query(query).get('rows')

    def _compute_conditions(self, filters, extra_conditions):
        conditions = extra_conditions or []

        if filters is not None and len(filters) > 0:
            conditions.extend([self._generate_condition(key, value) for key, value in sorted(filters.items())])

        return conditions

    @staticmethod
    def _generate_condition(key, value):
        if isinstance(value, list):
            value_list = ','.join(["'" + v + "'" for v in value])
            return "t.{} IN ({})".format(key, value_list)

        return "t.{} = '{}'".format(key, value)

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance

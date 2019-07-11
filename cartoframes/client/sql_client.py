from __future__ import absolute_import

from carto.exceptions import CartoException

from .internal import create_client


class SQLClient(object):
    """
    TODO
    """

    def __init__(self, credentials, session=None):
        self._is_org_user = None
        self._creds = credentials
        self._client = create_client(credentials, session)

    def query(self, query, verbose=False):
        """
        TODO
        """
        try:
            response = self._client.execute_query(query)
            if not verbose:
                return response.get('rows')
            else:
                return response
        except CartoException as e:
            print('Error: {}'.format(e))

    def execute(self, query):
        """
        TODO
        """
        try:
            return self._client.execute_long_running_query(query)
        except CartoException as e:
            print('Error: {}'.format(e))

    def distinct(self, table_name, column_name):
        query = 'SELECT DISTINCT {0} FROM {1};'.format(column_name, table_name)
        output = self.query(query)
        return list(map(lambda x: x.get(column_name), output))

    def count(self, table_name):
        query = 'SELECT COUNT(*) FROM {};'.format(table_name)
        output = self.query(query)
        return output[0].get('count')

    def bounds(self, query):
        output = self.query('''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM ({}) q
            ) q;
        '''.format(query))
        return output[0].get('bounds')

    def create_table(self, table_name, columns, cartodbfy=True):
        is_org_user = self._check_org_user()
        query = 'BEGIN;'
        query += 'CREATE TABLE {0} ({1});'.format(
            table_name,
            ','.join(map(lambda x: ' '.join(x), columns)))
        if cartodbfy:
            query += 'SELECT CDB_CartoDBFyTable(\'{0}\', \'{1}\');'.format(
                self._creds.username() if is_org_user else 'public',
                table_name)
        query += 'COMMIT;'
        print(query)
        return self.execute(query)

    def drop_table(self, table_name):
        return self.execute('DROP TABLE {0};'.format(table_name))

    def _check_org_user(self):
        """Report whether user is in a multiuser CARTO organization or not"""
        if self._is_org_user is None:
            query = 'SELECT unnest(current_schemas(\'f\'))'
            res = self._client.execute_query(query, do_post=False)
            self._is_org_user = res['rows'][0]['unnest'] != 'public'
        return self._is_org_user

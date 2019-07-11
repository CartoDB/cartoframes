from __future__ import absolute_import

from carto.exceptions import CartoException

from .internal import create_client


class SQLClient(object):
    """SQLClient class is a client to run SQL queries in a CARTO account.

    Args:
        creds (:py:class:`Credentials <cartoframes.auth.Credentials>`):
          A :py:class:`Credentials <cartoframes.auth.Credentials>`
          instance can be used in place of a `base_url`/`api_key` combination.
        session (requests.Session, optional): requests session. See `requests
          documentation
          <http://docs.python-requests.org/en/master/user/advanced/>`__
          for more information.

    Example:

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.client import SQLClient

            creds = Credentials(username='<YOUR USER NAME>', api_key='<YOUR API KEY>')
            sql_client = SQLClient(creds)

            sql_client.query('SELECT * FROM table_name')
            sql_client.execute('DROP TABLE table_name')

            sql_client.distinct('table_name', 'column_name')
            sql_client.count('table_name')
            ...
    """

    def __init__(self, credentials, session=None):
        self._is_org_user = None
        self._creds = credentials
        self._client = create_client(credentials, session)

    def query(self, query, verbose=False):
        """Run a SQL query. It returns a JSON object with the response.
        If the `verbose` params is True it returns the full SQL response.
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
        """Run a long running query. It returns an object with the
        status and information of the job."""
        try:
            return self._client.execute_long_running_query(query)
        except CartoException as e:
            print('Error: {}'.format(e))

    def distinct(self, table_name, column_name):
        """Get the distict values and their count in a table
        for a specific column."""
        query = '''
        SELECT {0}, COUNT(*) FROM {1}
        GROUP BY {0} ORDER BY 2 DESC
        '''.format(column_name, table_name)
        output = self.query(query)
        return list(map(lambda x: (x.get(column_name), x.get('count')), output))

    def count(self, table_name):
        """Get the number of elements of a table."""
        query = 'SELECT COUNT(*) FROM {};'.format(table_name)
        output = self.query(query)
        return output[0].get('count')

    def bounds(self, query):
        """Get the bounds of the geometries in a table."""
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
        """Create a table with a specific table name and columns.
        By default, geometry columns are added to the table.
        To disable this pass `cartodbfy=False`.
        """
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

    def rename_table(self, table_name, new_table_name):
        """Rename a table from its table name."""
        return self.execute('ALTER TABLE {0} RENAME TO {1};'.format(table_name, new_table_name))

    def drop_table(self, table_name):
        """Remove a table from its table name."""
        return self.execute('DROP TABLE {0};'.format(table_name))

    def _check_org_user(self):
        """Report whether user is in a multiuser CARTO organization or not"""
        if self._is_org_user is None:
            query = 'SELECT unnest(current_schemas(\'f\'))'
            res = self._client.execute_query(query, do_post=False)
            self._is_org_user = res['rows'][0]['unnest'] != 'public'
        return self._is_org_user

from ...io.managers.context_manager import ContextManager

COLLISION_STRATEGIES = ['fail', 'replace']


class SQLClient:
    """SQLClient class is a client to run SQL queries in a CARTO account.
    It also provides basic SQL utilities for analyzing and managing tables.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`):
            A :py:class:`Credentials <cartoframes.auth.Credentials>`
            instance can be used in place of a `username`|`base_url` / `api_key` combination.

    Example:
        >>> sql = SQLClient(credentials)

    """
    def __init__(self, credentials=None):
        self._context_manager = ContextManager(credentials)

    def query(self, query, verbose=False):
        """Run a SQL query. It returns a `list` with content of the response.
        If the `verbose` param is True it returns the full SQL response in a `dict`.
        For more information check the `SQL API
        documentation
        <https://carto.com/developers/sql-api/reference/#tag/Single-SQL-Statement>`.

        Args:
            query (str): SQL query.
            verbose (bool, optional): flag to return all the response. Default False.

        Example:
            >>> sql.query('SELECT * FROM table_name')

        """
        response = self._context_manager.execute_query(query.strip())
        if not verbose:
            return response.get('rows')
        else:
            return response

    def execute(self, query):
        """Run a long running query. It returns an object with the
        status and information of the job. For more information check the `Batch API
        documentation
        <https://carto.com/developers/sql-api/reference/#tag/Batch-Queries>`.

        Args:
            query (str): SQL query.

        Example:
            >>> sql.execute('DROP TABLE table_name')

        """
        return self._context_manager.execute_long_running_query(query.strip())

    def distinct(self, table_name, column_name):
        """Get the distict values and their count in a table
        for a specific column.

        Args:
            table_name (str): name of the table.
            column_name (str): name of the column.

        Example:
            >>> sql.distinct('table_name', 'column_name')
            [('value1', 10), ('value2', 5)]

        """
        query = '''
            SELECT {0}, COUNT(*) FROM {1}
            GROUP BY 1 ORDER BY 2 DESC
        '''.format(column_name, table_name)
        output = self.query(query)
        return [(x.get(column_name), x.get('count')) for x in output]

    def count(self, table_name):
        """Get the number of elements of a table.

        Args:
            table_name (str): name of the table.

        Example:
            >>> sql.count('table_name')
            15

        """
        query = 'SELECT COUNT(*) FROM {};'.format(table_name)
        output = self.query(query)
        return output[0].get('count')

    def bounds(self, table_name):
        """Get the bounds of the geometries in a table.

        Args:
            table_name (str): name of the table containing a "the_geom" column.

        Example:
            >>> sql.bounds('table_name')
            [[-1,-1], [1,1]]

        """
        query = '''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM (SELECT the_geom FROM {}) q
            ) q;
        '''.format(table_name)
        output = self.query(query)
        return output[0].get('bounds')

    def schema(self, table_name, raw=False):
        """Show information about the schema of a table.

        Args:
            table_name (str): name of the table.
            raw (bool, optional): return raw dict data if set to True.
                Default False.

        Example:
            >>> sql.schema('table_name')
            Column name          Column type
            -------------------------------------
            cartodb_id           number
            the_geom             geometry
            the_geom_webmercator geometry
            column1              string
            column2              number

        """
        query = 'SELECT * FROM {0} LIMIT 0;'.format(table_name)
        output = self.query(query, verbose=True)
        fields = output.get('fields')
        if raw is True:
            return {key: fields[key]['type'] for key in fields}
        else:
            columns = ['Column name', 'Column type']
            rows = [(key, fields[key]['type']) for key in fields]
            self._print_table(rows, columns=columns, padding=[10, 5])
            return None

    def describe(self, table_name, column_name):
        """Show information about a column in a specific table.
        It returns the COUNT of the table. If the column type is number
        it also returns the AVG, MIN and MAX.

        Args:
            table_name (str): name of the table.
            column_name (str): name of the column.

        Example:
            >>> sql.describe('table_name', 'column_name')
            count     1.00e+03
            avg       2.00e+01
            min       0.00e+00
            max       5.00e+01
            type: number

        """
        column_type = self._get_column_type(table_name, column_name)
        stats = ['COUNT(*)']
        if column_type == 'number':
            stats.append('AVG({})'.format(column_name))
            stats.append('MIN({})'.format(column_name))
            stats.append('MAX({})'.format(column_name))
        query = '''
            SELECT {0}
            FROM {1};
        '''.format(','.join(stats), table_name)
        output = self.query(query, verbose=True)
        fields = output.get('rows')[0]
        rows = [(key, '{:0.2e}'.format(fields[key])) for key in fields if fields[key] is not None]
        self._print_table(rows, padding=[5, 10])
        print('type: {}'.format(column_type))

    def create_table(self, table_name, columns_types, if_exists='fail', cartodbfy=True):
        """Create a table with a specific table name and columns.

        Args:
            table_name (str): name of the table.
            column_types (dict): dictionary with the column names and types.
            if_exists (str, optional): collision strategy if the table already exists in CARTO.
                Options are 'fail' or 'replace'. Default 'fail'.
            cartodbfy (bool, optional): convert the table to CARTO format.
                Default True. More info `here
                <https://carto.com/developers/sql-api/guides/creating-tables/#create-tables>`.

        Example:
            >>> sql.create_table('table_name', {'column1': 'text', 'column2': 'integer'})

        """
        if not isinstance(columns_types, dict):
            raise ValueError('The columns_types parameter should be a dictionary of column names and types.')

        if if_exists not in COLLISION_STRATEGIES:
            raise ValueError('Please provide a valid if_exists value among {}'.format(', '.join(COLLISION_STRATEGIES)))

        columns = ['{0} {1}'.format(cname, ctype) for cname, ctype in columns_types.items()]
        schema = self._context_manager.get_schema()
        query = '''
            BEGIN;
            {drop};
            {create};
            {cartodbfy};
            COMMIT;
        '''.format(
            drop='DROP TABLE IF EXISTS {}'.format(table_name) if if_exists == 'replace' else '',
            create='CREATE TABLE {0} ({1})'.format(table_name, ','.join(columns)),
            cartodbfy='SELECT CDB_CartoDBFyTable(\'{0}\', \'{1}\')'.format(
                schema, table_name) if cartodbfy else ''
        )
        self.execute(query)

    def insert_table(self, table_name, columns_values):
        """Insert a row to the table.

        Args:
            table_name (str): name of the table.
            columns_values (dict): dictionary with the column names and values.
        Example:
            >>> sql.insert_table('table_name', {'column1': ['value1', 'value2'], 'column2': [1, 2]})

        """
        cnames = columns_values.keys()
        cvalues = [self._row_values_format(v) for v in zip(*columns_values.values())]
        query = '''
            INSERT INTO {0} ({1}) VALUES {2};
        '''.format(table_name, ','.join(cnames), ','.join(cvalues))
        self.execute(query)

    def update_table(self, table_name, column_name, column_value, condition):
        """Update the column's value for the rows that match the condition.

        Args:
            table_name (str): name of the table.
            column_name (str): name of the column.
            column_value (str): value of the column.
            condition (str): "where" condition of the request.

        Example:
            >>> sql.update_table('table_name', 'column1', 'VALUE1', 'column1=\'value1\'')

        """
        value = self._sql_format(column_value)
        query = '''
            UPDATE {0} SET {1}={2} WHERE {3};
        '''.format(table_name, column_name, value, condition)
        self.execute(query)

    def rename_table(self, table_name, new_table_name):
        """Rename a table from its table name.

        Args:
            table_name (str): name of the original table.
            new_table_name (str): name of the new table.

        Example:
            >>> sql.rename_table('table_name', 'table_name2')

        """
        query = 'ALTER TABLE {0} RENAME TO {1};'.format(table_name, new_table_name)
        self.execute(query)

    def drop_table(self, table_name):
        """Remove a table from its table name.

        Args:
            table_name (str): name of the table.

        Example:
            >>> sql.drop_table('table_name')

        """
        query = 'DROP TABLE IF EXISTS {0};'.format(table_name)
        self.execute(query)

    def _get_column_type(self, table_name, column_name):
        query = 'SELECT {0} FROM {1} LIMIT 0;'.format(column_name, table_name)
        output = self.query(query, verbose=True)
        fields = output.get('fields')
        field = fields.get(column_name)
        return field.get('type')

    def _sql_format(self, value):
        if isinstance(value, str):
            return '\'{}\''.format(value)
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        return str(value)

    def _row_values_format(self, row_values):
        return '({})'.format(','.join([self._sql_format(value) for value in row_values]))

    def _print_table(self, rows, columns=None, padding=None):
        row_format = ''
        index = 0
        for column in columns or rows[0]:
            length = str(len(str(column)) + (padding[index] if padding else 5))
            row_format += '{:' + length + '}'
            index += 1
        if columns:
            header = row_format.format(*columns)
            print(header)
            print('-' * len(header))
        for row in rows:
            print(row_format.format(*row))

from abc import ABCMeta, abstractmethod

class DatasetBase():
    __metaclass__ = ABCMeta

    FAIL = 'fail'
    REPLACE = 'replace'
    APPEND = 'append'

    PRIVATE = DatasetInfo.PRIVATE
    PUBLIC = DatasetInfo.PUBLIC
    LINK = DatasetInfo.LINK

    STATE_LOCAL = 'local'
    STATE_REMOTE = 'remote'

    GEOM_TYPE_POINT = 'point'
    GEOM_TYPE_LINE = 'line'
    GEOM_TYPE_POLYGON = 'polygon'

    def __init__(self, context=None):
        from ..auth import _default_context
        self._context = context or _default_context
        self._client = self._create_client()
        self._table_name = None
        self._schema = None

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @property
    def context(self):
        """Dataset :py:class:`Context <cartoframes.auth.Context>`"""
        return self._context

    @context.setter
    def context(self, context):
        """Set a new :py:class:`Context <cartoframes.auth.Context>` for a Dataset instance."""
        self._context = context
        self._schema = context.get_default_schema()
        self._client = self._create_client()

    @property
    def table_name(self):
        """Dataset table name"""
        return self._table_name

    @table_name.setter
    def table_name(self, table_name):
        self._table_name = normalize_name(table_name)

    @property
    def schema(self):
        """Dataset schema"""
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    def _create_client(self):
        if self._context:
            return create_client(self._context.creds, self._context.session)

    def exists(self):
        """Checks to see if table exists"""
        try:
            self._client.execute_query(
                'EXPLAIN SELECT * FROM "{table_name}"'.format(table_name=self._table_name),
                do_post=False)
            return True
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            self._context._debug_print(err=err)
            return False

    def _cartodbfy_query(self):
        return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
            .format(schema=self._schema or self._get_schema(), table_name=self._table_name)

    def _drop_table_query(self, if_exists=True):
        return '''DROP TABLE {if_exists} {table_name}'''.format(
            table_name=self._table_name,
            if_exists='IF EXISTS' if if_exists else '')

    def _already_exists_error(self):
        return CartoException('Table with name {t} and schema {s} already exists in CARTO.'
                              'Please choose a different `table_name` or use '
                              'if_exists="replace" to overwrite it'.format(
                                  t=self._table_name, s=self._schema))

    def _is_ready_for_upload_validation(self):
        if self._table_name is None or self._context is None:
            raise ValueError('You should provide a table_name and context to upload data.')

    def _is_ready_for_dowload_validation(self):
        if self._context is None or (self._table_name is None and self._query is None):
            raise ValueError('You should provide a context and a table_name or query to download data.')

    def _copyto(self, columns, query, limit, decode_geom, retry_times):
        copy_query = """COPY ({}) TO stdout WITH (FORMAT csv, HEADER true)""".format(query)
        raw_result = self._client.download(copy_query, retry_times)

        df_types = dtypes(columns, exclude_dates=True, exclude_the_geom=True, exclude_bools=True)
        date_column_names = date_columns_names(columns)
        bool_column_names = bool_columns_names(columns)

        converters = {'the_geom': lambda x: decode_geometry(x, ENC_WKB_BHEX) if decode_geom else x}
        for bool_column_name in bool_column_names:
            converters[bool_column_name] = lambda x: convert_bool(x)

        df = pd.read_csv(raw_result, dtype=df_types,
                         parse_dates=date_column_names,
                         true_values=['t'],
                         false_values=['f'],
                         index_col='cartodb_id' if 'cartodb_id' in df_types else False,
                         converters=converters)

        if decode_geom:
            df.rename({'the_geom': 'geometry'}, axis='columns', inplace=True)

        return df

    def get_query_columns(self):
        query = 'SELECT * FROM ({}) _q LIMIT 0'.format(self.get_query())
        table_info = self._client.execute_query(query)
        return Column.from_sql_api_fields(table_info['fields'])

    def get_query(self):
        if self.query:
            return self._query
        else:
            return compute_query(self)

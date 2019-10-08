# coding=UTF-8

import re
import sys

from unidecode import unidecode

from .geom_utils import detect_encoding_type, decode_geometry


class Column(object):
    DATETIME_DTYPES = ['datetime64[D]', 'datetime64[ns]', 'datetime64[ns, UTC]']
    SUPPORTED_GEOM_COL_NAMES = ['the_geom', 'geom', 'geometry']
    FORBIDDEN_COLUMN_NAMES = ['the_geom_webmercator']
    MAX_LENGTH = 63
    MAX_COLLISION_LENGTH = MAX_LENGTH - 4
    RESERVED_WORDS = ('ALL', 'ANALYSE', 'ANALYZE', 'AND', 'ANY', 'ARRAY', 'AS', 'ASC', 'ASYMMETRIC', 'AUTHORIZATION',
                      'BETWEEN', 'BINARY', 'BOTH', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'CONSTRAINT',
                      'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_ROLE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
                      'CURRENT_USER', 'DEFAULT', 'DEFERRABLE', 'DESC', 'DISTINCT', 'DO', 'ELSE', 'END', 'EXCEPT',
                      'FALSE', 'FOR', 'FOREIGN', 'FREEZE', 'FROM', 'FULL', 'GRANT', 'GROUP', 'HAVING', 'ILIKE', 'IN',
                      'INITIALLY', 'INNER', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN', 'LEADING', 'LEFT', 'LIKE',
                      'LIMIT', 'LOCALTIME', 'LOCALTIMESTAMP', 'NATURAL', 'NEW', 'NOT', 'NOTNULL', 'NULL', 'OFF',
                      'OFFSET', 'OLD', 'ON', 'ONLY', 'OR', 'ORDER', 'OUTER', 'OVERLAPS', 'PLACING', 'PRIMARY',
                      'REFERENCES', 'RIGHT', 'SELECT', 'SESSION_USER', 'SIMILAR', 'SOME', 'SYMMETRIC', 'TABLE', 'THEN',
                      'TO', 'TRAILING', 'TRUE', 'UNION', 'UNIQUE', 'USER', 'USING', 'VERBOSE', 'WHEN', 'WHERE',
                      'XMIN', 'XMAX', 'FORMAT', 'CONTROLLER', 'ACTION', )

    @staticmethod
    def from_sql_api_fields(sql_api_fields):
        return [Column(column, normalize=False, pgtype=sql_api_fields[column]['type']) for column in sql_api_fields]

    def __init__(self, name, normalize=True, pgtype=None):
        if not name:
            raise ValueError('Column name cannot be null or empty')

        self.name = str(name)
        self.pgtype = pgtype
        self.dtype = pg2dtypes(pgtype)
        if normalize:
            self.normalize()

    def normalize(self, forbidden_column_names=None):
        self._sanitize()
        self.name = self._truncate()

        if forbidden_column_names:
            i = 1
            while self.name in forbidden_column_names:
                self.name = '{}_{}'.format(self._truncate(length=Column.MAX_COLLISION_LENGTH), str(i))
                i += 1

        return self

    def _sanitize(self):
        self.name = self._slugify(self.name)

        if self._is_reserved() or self._is_unsupported():
            self.name = '_{}'.format(self.name)

    def _is_reserved(self):
        return self.name.upper() in Column.RESERVED_WORDS

    def _is_unsupported(self):
        return not re.match(r'^[a-z_]+[a-z_0-9]*$', self.name)

    def _truncate(self, length=MAX_LENGTH):
        return self.name[:length]

    def _slugify(self, value):
        value = str(value).lower()

        if sys.version_info[0] < 3:
            value = unidecode(value.decode('utf-8'))
        else:
            value = unidecode(value)

        value = re.sub(r'<[^>]+>', '', value)
        value = re.sub(r'&.+?;', '-', value)
        value = re.sub(r'[^a-z0-9 _-]', '-', value).strip().lower()
        value = re.sub(r'\s+', '-', value)
        value = re.sub(r' ', '-', value)
        value = re.sub(r'-+', '-', value)
        value = re.sub(r'-', '_', value)

        return value


class DataframeColumnInfo(object):
    def __init__(self, column, geom_column=None, geom_type=None, dtype=None):
        if column:
            self.dataframe = column
            self.database = self._database_column_name(geom_column)
            self.database_type = self._db_column_type(geom_column, geom_type, dtype)
        else:
            self.dataframe = None
            self.database = 'the_geom'
            self.database_type = 'geometry(Point, 4326)'

    def _database_column_name(self, geom_column):
        if geom_column and self.dataframe == geom_column:
            normalized_name = 'the_geom'
        else:
            normalized_name = normalize_name(self.dataframe)

        return normalized_name

    def _db_column_type(self, geom_column, geom_type, dtype):
        if geom_column and self.dataframe == geom_column:
            db_type = 'geometry({}, 4326)'.format(geom_type or 'Point')
        else:
            db_type = _dtypes2pg(dtype)

        return db_type

    def __eq__(self, obj):
        if isinstance(obj, dict):
            return self.dataframe == obj['dataframe'] and \
                   self.database == obj['database'] and \
                   self.database_type == obj['database_type']
        else:
            return self.dataframe == obj.dataframe and \
                   self.database == obj.database and \
                   self.database_type == obj.database_type


class DataframeColumnsInfo(object):
    def __init__(self, df, with_lnglat=None):
        self.df = df
        self.with_lnglat = with_lnglat

        self.geom_column = self._get_geom_col_name()
        geom_type, enc_type = self._get_geometry_type()
        self.geom_type = geom_type
        self.enc_type = enc_type

        self.columns = self._get_columns_info()

    def _get_columns_info(self):
        columns = []
        for c in self.df.columns:
            if self._filter_column(c):
                continue

            columns.append(DataframeColumnInfo(c, self.geom_column, self.geom_type, self.df.dtypes[c]))

        if self.with_lnglat:
            columns.append(DataframeColumnInfo(None))

        return columns

    def _filter_column(self, column):
        return column.lower() in Column.FORBIDDEN_COLUMN_NAMES or (self.with_lnglat and column == self.geom_column)

    def _get_geom_col_name(self):
        geom_col = getattr(self.df, '_geometry_column_name', None)
        if geom_col is None:
            try:
                df_columns = [x.lower() for x in self.df.columns]
                geom_col = next(x for x in Column.SUPPORTED_GEOM_COL_NAMES if x in df_columns)
            except StopIteration:
                pass

        return geom_col

    def _get_geometry_type(self):
        if self.geom_column is not None:
            first_geom = _first_value(self.df[self.geom_column])
            if first_geom:
                enc_type = detect_encoding_type(first_geom)
                geom = decode_geometry(first_geom, enc_type)
                return geom.geom_type, enc_type

        return None, None


def normalize_names(column_names):
    """Given an arbitrary column name, translate to a SQL-normalized column
        name a la CARTO's Import API will translate to

        Examples
            * 'Field: 2' -> 'field_2'
            * '2 Items' -> '_2_items'
            * 'Unnamed: 0' -> 'unnamed_0',
            * '201moore' -> '_201moore',
            * '201moore' -> '_201moore_1',
            * 'Acadia 1.2.3' -> 'acadia_1_2_3',
            * 'old_soaker' -> 'old_soaker',
            * '_testingTesting' -> '_testingtesting',
            * 1 -> '_1',
            * 1.0 -> '_1_0',
            * 'public' -> 'public',
            * 'SELECT' -> '_select',
            * 'à' -> 'a',
            * 'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabesplittedrightnow' -> \
             'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabespli',
            * 'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabesplittedrightnow' -> \
             'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabe_1',
            * 'all' -> '_all'

        Args:
            column_names (list): List of column names that will be SQL normalized
        Returns:
            list: List of SQL-normalized column names
    """
    result = []
    for column_name in column_names:
        column = Column(column_name).normalize(forbidden_column_names=result)
        result.append(column.name)

    return result


def normalize_name(column_name):
    if column_name is None:
        return None

    return normalize_names([column_name])[0]


def dtypes(columns, exclude_dates=False, exclude_the_geom=False, exclude_bools=False):
    return {x.name: x.dtype if not x.name == 'cartodb_id' else 'int64'
            for x in columns if not (exclude_dates is True and x.dtype in Column.DATETIME_DTYPES)
            and not(exclude_the_geom is True and x.name in Column.SUPPORTED_GEOM_COL_NAMES)
            and not(exclude_bools is True and x.dtype == 'bool')}


def date_columns_names(columns):
    return [x.name for x in columns if x.dtype in Column.DATETIME_DTYPES]


def bool_columns_names(columns):
    return [x.name for x in columns if x.dtype == 'bool']


def pg2dtypes(pgtype):
    """Returns equivalent dtype for input `pgtype`."""
    mapping = {
        'bigint': 'float64',
        'boolean': 'bool',
        'date': 'datetime64[D]',
        'double precision': 'float64',
        'geometry': 'object',
        'int': 'int64',
        'integer': 'float64',
        'number': 'float64',
        'numeric': 'float64',
        'real': 'float64',
        'smallint': 'float64',
        'string': 'object',
        'timestamp': 'datetime64[ns]',
        'timestampz': 'datetime64[ns]',
        'timestamp with time zone': 'datetime64[ns]',
        'timestamp without time zone': 'datetime64[ns]',
        'USER-DEFINED': 'object',
    }
    return mapping.get(str(pgtype), 'object')


def _dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'float64': 'numeric',
        'int64': 'bigint',
        'float32': 'numeric',
        'int32': 'integer',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
        'datetime64[ns, UTC]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')


def _first_value(series):
    series = series.loc[~series.isnull()]  # Remove null values
    if len(series) > 0:
        return series.iloc[0]

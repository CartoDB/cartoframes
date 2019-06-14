# coding=UTF-8

import re
import sys

from unidecode import unidecode


class Column(object):
    DATETIME_DTYPES = ['datetime64[D]', 'datetime64[ns]', 'datetime64[ns, UTC]']
    SUPPORTED_GEOM_COL_NAMES = ['geom', 'the_geom', 'geometry']
    RESERVED_COLUMN_NAMES = SUPPORTED_GEOM_COL_NAMES + ['the_geom_webmercator', 'cartodb_id']
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

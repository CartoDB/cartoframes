# coding=UTF-8

import re

from unidecode import unidecode

from .utils import dtypes2pg, pg2dtypes, PG_NULL

BOOL_DBTYPES = ['bool', 'boolean']
INT_DBTYPES = ['int2', 'int4', 'int2', 'int', 'int8', 'smallint', 'integer', 'bigint']
FLOAT_DBTYPES = ['float4', 'float8', 'real', 'double precision', 'numeric', 'decimal']
DATETIME_DBTYPES = ['date', 'timestamp', 'timestampz']
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
                  'XMIN', 'XMAX', 'FORMAT', 'CONTROLLER', 'ACTION')


class ColumnInfo:

    def __init__(self, name, dbname, dbtype, is_geom):
        self.name = name
        self.dbname = dbname
        self.dbtype = dbtype
        self.is_geom = is_geom

    def __repr__(self):
        params = ', '.join([self.name, self.dbname, self.dbtype, str(self.is_geom)])
        return 'ColumnInfo({})'.format(params)

    def __eq__(self, other):
        return self.dbname == other.dbname and \
                self.dbtype == other.dbtype and \
                self.is_geom == other.is_geom

    def __gt__(self, other):
        return self.dbname > other.dbname

    def __ge__(self, other):
        return self.dbname >= other.dbname

    def __lt__(self, other):
        return self.dbname < other.dbname

    def __le__(self, other):
        return self.dbname <= other.dbname


def get_dataframe_columns_info(df):
    columns = []

    for name in df.columns:
        if _is_valid_column(name):
            dbtype = dtypes2pg(str(df.dtypes[name]))
            columns.append(_create_column_info(name, dbtype))

    return columns


def get_query_columns_info(fields):
    columns = []

    for name in fields:
        field = fields[name]
        pgtype = field.get('pgtype')
        dbtype = dtypes2pg(pg2dtypes(pgtype)) if pgtype else field.get('type')
        columns.append(_create_column_info(name, dbtype))

    return columns


def _is_valid_column(name):
    return name.lower() not in FORBIDDEN_COLUMN_NAMES


def _create_column_info(name, dbtype=None):
    is_geom = False
    dbname = normalize_name(name)
    if dbtype == 'geometry':
        dbtype = 'geometry(Geometry, 4326)'
        is_geom = True
    return ColumnInfo(name, dbname, dbtype, is_geom)


def normalize_name(column_name):
    if column_name is None:
        return None

    return normalize_names([column_name])[0]


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
        result.append(_normalize(column_name, forbidden_column_names=result))

    return result


def _normalize(column_name, forbidden_column_names=None):
    column_name = _truncate(_sanitize(_slugify(column_name)))

    if forbidden_column_names:
        i = 1
        while column_name in forbidden_column_names:
            column_name = '{}_{}'.format(_truncate(column_name, length=MAX_COLLISION_LENGTH), i)
            i += 1

    return column_name


def _slugify(value):
    value = unidecode(str(value).lower())
    value = re.sub(r'<[^>]+>', '', value)
    value = re.sub(r'&.+?;', '-', value)
    value = re.sub(r'[^a-z0-9 _-]', '-', value).strip().lower()
    value = re.sub(r'\s+', '-', value)
    value = re.sub(r' ', '-', value)
    value = re.sub(r'-+', '-', value)
    value = re.sub(r'-', '_', value)
    return value


def _sanitize(value):
    return '_{}'.format(value) if _is_reserved(value) or _is_unsupported(value) else value


def _truncate(value, length=MAX_LENGTH):
    return value[:length]


def _is_reserved(value):
    return value.upper() in RESERVED_WORDS


def _is_unsupported(value):
    return not re.match(r'^[a-z_]+[a-z_0-9]*$', value)


def obtain_converters(columns):
    converters = {}

    for column in columns:
        if column.dbtype in INT_DBTYPES:
            converters[column.name] = _convert_int
        elif column.dbtype in FLOAT_DBTYPES:
            converters[column.name] = _convert_float
        elif column.dbtype in BOOL_DBTYPES:
            converters[column.name] = _convert_bool
        else:
            converters[column.name] = _convert_generic

    return converters


def date_columns_names(columns):
    return [x.name for x in columns if x.dbtype in DATETIME_DBTYPES]


def _convert_int(x):
    if _is_none_null(x):
        return None
    return int(x)


def _convert_float(x):
    if _is_none_null(x):
        return None
    return float(x)


def _convert_bool(x):
    if _is_none_null(x):
        return None
    if x == 't':
        return True
    if x == 'f':
        return False
    return bool(x)


def _convert_generic(x):
    if _is_none_null(x):
        return None
    return x


def _is_none_null(x):
    return x is None or x == PG_NULL

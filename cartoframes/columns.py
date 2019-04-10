# coding=UTF-8

import unicodedata
import re


class Column(object):
    MAX_LENGTH = 63
    MAX_COLLISION_LENGTH = 60
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

    def __init__(self, name):
        if not name:
            raise ValueError('Column name cannot be null or empty')

        self.name = str(name)

    def normalize(self, other_columns):
        self._sanitize()
        self._truncate()
        i = 1
        while self.name in other_columns:
            self.name = '{}_{}'.format(self._truncate(length=Column.MAX_LENGTH - 3), str(i))
            i += 1

        return self.name

    def _sanitize(self):
        self.name = self._slugify(self.name)

        if self._is_reserved() or self._is_unsupported():
            self.name = '_{}'.format(self.name)
        else:
            self.name

    def _is_reserved(self):
        return self.name.upper() in Column.RESERVED_WORDS

    def _is_unsupported(self):
        return not re.match(r'^[a-zA-Z_]+[a-zA-Z_0-9]*$', self.name)

    def _truncate(self, length=MAX_LENGTH):
        return self.name[:length]

    def _slugify(self, value, allow_unicode=False):
        value = str(value).decode()
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value).strip().lower()
        return re.sub(r'[-\s]+', '_', value)

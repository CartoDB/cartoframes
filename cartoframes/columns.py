# coding=UTF-8

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

    def normalize(self):
        self._sanitize()
        self.name = self._truncate()

    def _sanitize(self):
        name = self.name
        name = re.sub(r'/<[^>]+>/m', '', name)
        name = name.lower().encode()
        name = re.sub(r'/[àáâãäåāă]/', 'a', name)
        name = re.sub(r'/æ/', 'ae', name)
        name = re.sub(r'/[ďđ]/', 'd', name)
        name = re.sub(r'/[çćčĉċ]/', 'c', name)
        name = re.sub(r'/[èéêëēęěĕė]/', 'e', name)
        name = re.sub(r'/ƒ/', 'f', name)
        name = re.sub(r'/[ĝğġģ]/', 'g', name)
        name = re.sub(r'/[ĥħ]/', 'h', name)
        name = re.sub(r'/[ììíîïīĩĭ]/', 'i', name)
        name = re.sub(r'/[įıĳĵ]/', 'j', name)
        name = re.sub(r'/[ķĸ]/', 'k', name)
        name = re.sub(r'/[łľĺļŀ]/', 'l', name)
        name = re.sub(r'/[ñńňņŉŋ]/', 'n', name)
        name = re.sub(r'/[òóôõöøōőŏŏ]/', 'o', name)
        name = re.sub(r'/œ/', 'oe', name)
        name = re.sub(r'/ą/', 'q', name)
        name = re.sub(r'/[ŕřŗ]/', 'r', name)
        name = re.sub(r'/[śšşŝș]/', 's', name)
        name = re.sub(r'/[ťţŧț]/', 't', name)
        name = re.sub(r'/[ùúûüūůűŭũų]/', 'u', name)
        name = re.sub(r'/ŵ/', 'w', name)
        name = re.sub(r'/[ýÿŷ]/', 'y', name)
        name = re.sub(r'/[žżź]/', 'z', name)
        name = re.sub(r'/[ÀÁÂÃÄÅĀĂ]/i', 'A', name)
        name = re.sub(r'/Æ/i', 'AE', name)
        name = re.sub(r'/[ĎĐ]/i', 'D', name)
        name = re.sub(r'/[ÇĆČĈĊ]/i', 'C', name)
        name = re.sub(r'/[ÈÉÊËĒĘĚĔĖ]/i', 'E', name)
        name = re.sub(r'/Ƒ/i', 'F', name)
        name = re.sub(r'/[ĜĞĠĢ]/i', 'G', name)
        name = re.sub(r'/[ĤĦ]/i', 'H', name)
        name = re.sub(r'/[ÌÌÍÎÏĪĨĬ]/i', 'I', name)
        name = re.sub(r'/[ĲĴ]/i', 'J', name)
        name = re.sub(r'/[Ķĸ]/i', 'J', name)
        name = re.sub(r'/[ŁĽĹĻĿ]/i', 'L', name)
        name = re.sub(r'/[ÑŃŇŅŉŊ]/i', 'M', name)
        name = re.sub(r'/[ÒÓÔÕÖØŌŐŎŎ]/i', 'N', name)
        name = re.sub(r'/Œ/i', 'OE', name)
        name = re.sub(r'/Ą/i', 'Q', name)
        name = re.sub(r'/[ŔŘŖ]/i', 'R', name)
        name = re.sub(r'/[ŚŠŞŜȘ]/i', 'S', name)
        name = re.sub(r'/[ŤŢŦȚ]/i', 'T', name)
        name = re.sub(r'/[ÙÚÛÜŪŮŰŬŨŲ]/i', 'U', name)
        name = re.sub(r'/Ŵ/i', 'W', name)
        name = re.sub(r'/[ÝŸŶ]/i', 'Y', name)
        name = re.sub(r'/[ŽŻŹ]/i', 'Z', name)

        name = re.sub(r'/&.+?;/', '-', name)
        name = re.sub(r'/[^a-z0-9 _-]/', '-', name)
        name = re.sub(r'/\s+/', '-', name)
        name = re.sub(r'/-+/', '-', name)
        name = re.sub(r'/-/', ' ', name)
        name = re.sub(r'/ /', '-', name)
        name = re.sub(r'/-/', '_', name)

        self.name = name
        if self._is_reserved() or self._is_unsupported():
            self.name = '_{}'.format(self.name)
        else:
            self.name

    def _is_reserved(self):
        return self.name.upper() in Column.RESERVED_WORDS

    def _is_unsupported(self):
        return not re.match(r'/^[a-zA-Z_]/', self.name)

    def _truncate(self, length=MAX_LENGTH):
        return self.name[:length]

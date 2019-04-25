from __future__ import absolute_import
from .source import Source


class SQL(Source):
    """
      TODO
    """

    def __init__(self, query):
        super(SQL, self).__init__(query=query)
from __future__ import absolute_import


class Source(object):
    "Parent class for sources"

    def __init__(self, query, bounds=None):
        self.query = query
        self.bounds = bounds

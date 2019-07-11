from __future__ import absolute_import

from .internal import create_client


class SQLClient(object):
    """
    TODO
    """

    def __init__(self, credentials, session=None):
        self._client = create_client(credentials, session)

    def query(self, query):
        """
        TODO
        """
        return self._client.execute_query(query)

    def execute(self, query):
        """
        TODO
        """
        return self._client.execute_long_running_query(query)




from __future__ import absolute_import

from carto.exceptions import CartoException

from .internal import create_client


class SQLClient(object):
    """
    TODO
    """

    def __init__(self, credentials, session=None):
        self._client = create_client(credentials, session)

    def query(self, query, verbose=False):
        """
        TODO
        """
        try:
            response = self._client.execute_query(query)
            if not verbose:
                return response.get('rows')
            else:
                return response
        except CartoException as e:
            raise ValueError(e)
            print('Error: {}'.format(e))

    def execute(self, query):
        """
        TODO
        """
        try:
            return self._client.execute_long_running_query(query)
        except CartoException as e:
            print('Error: {}'.format(e))




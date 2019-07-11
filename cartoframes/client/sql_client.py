from __future__ import absolute_import

from ..client import create_client


class SQLClient(object):
    """
    TODO
    """

    def __init__(self, credentials, session=None):
        self._client = create_client(credentials, session)

    def query(self):
        """
        TODO
        """
        pass

    def execute(self):
        """
        TODO
        """
        pass

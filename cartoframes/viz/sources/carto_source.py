from .base_source import BaseSource
from ...io.managers.context_manager import ContextManager

SOURCE_TYPE = 'Query'


class CartoSource(BaseSource):
    """CartoSource

    Args:
        data (str): a CARTO table name, CARTO SQL query.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. If not provided, the credentials will be automatically
            obtained from the default credentials if available.

    Example:

        Table name.

        >>> CartoSource('table_name')

        SQL query.

        >>> CartoSource('SELECT * FROM table_name')

        Setting the credentials.

        >>> CartoSource('table_name', credentials)

    """
    def __init__(self, data, credentials=None):
        if not isinstance(data, str):
            raise ValueError('Wrong source input. Valid values are str.')

        self.type = SOURCE_TYPE
        self.manager = ContextManager(credentials)
        self.query = self.manager.compute_query(data)
        self.credentials = self.manager.credentials

    def get_credentials(self):
        if self.credentials:
            return {
                # CARTO VL requires a username but CARTOframes allows passing only the base_url.
                # That's why 'user' is used by default if username is empty.
                'username': self.credentials.username or 'user',
                'api_key': self.credentials.api_key,
                'base_url': self.credentials.base_url
            }

    def get_geom_type(self):
        return self.manager.get_geom_type(self.query) or 'point'

    def compute_metadata(self, columns=None):
        self.data = self.query
        self.bounds = self.manager.get_bounds(self.query)

    def is_public(self):
        return self.manager.is_public(self.query)

    def schema(self):
        return self.manager.get_schema()

    def get_table_names(self):
        return self.manager.get_table_names(self.query)

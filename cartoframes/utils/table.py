from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager

from .. import __version__
from ..auth import get_default_credentials
from ..data import Dataset

from warnings import filterwarnings
filterwarnings("ignore", category=FutureWarning, module="carto")


def tables(credentials=None):
    """List all tables in user's CARTO account
    Returns:
        :obj:`list` of :py:class:`Dataset <cartoframes.data.Dataset>`
    """
    credentials = credentials or get_default_credentials()
    auth_client = _create_auth_client(credentials)
    table_names = DatasetManager(auth_client).filter(
        show_table_size_and_row_count='false',
        show_table='false',
        show_stats='false',
        show_likes='false',
        show_liked='false',
        show_permission='false',
        show_uses_builder_features='false',
        show_synchronization='false',
        load_totals='false')
    return [Dataset(str(table_name), credentials=credentials) for table_name in table_names]


def _create_auth_client(credentials):
    return APIKeyAuthClient(
        base_url=credentials.base_url,
        api_key=credentials.api_key,
        session=credentials.session,
        client_id='cartoframes_{}'.format(__version__),
        user_agent='cartoframes_{}'.format(__version__)
    )

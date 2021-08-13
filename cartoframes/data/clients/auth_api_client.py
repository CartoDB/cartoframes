from carto.api_keys import APIKeyManager

from ...auth import get_default_credentials
from ...utils.utils import create_hash


class AuthAPIClient:
    """AuthAPIClient class is a client of the CARTO Auth API.
    More info: https://carto.com/developers/auth-api/.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            credentials of user account. If not provided, a default credentials
            (if set with :py:meth:`set_default_credentials <cartoframes.auth.set_default_credentials>`)
            will attempted to be used.

    """

    def __init__(self, credentials=None):
        credentials = credentials or get_default_credentials()
        self._api_key_manager = _get_api_key_manager(credentials)

    def create_api_key(self, sources, apis=['sql', 'maps'], permissions=['select'], name=None):
        tables = []
        tables_names = []

        for source in sources:
            table_names = source.get_table_names()
            for table_name in table_names:
                tables.append(_get_table_dict(source.schema(), table_name, permissions))
                tables_names.append(table_name)

        tables_names.sort()
        gen_name = 'cartoframes_{}'.format(create_hash(tables_names))

        if name is None:
            name = gen_name

        try:
            # Try to create the API key
            api_key = self._api_key_manager.create(name, apis, tables)
        except Exception as e:
            if str(e) == 'Validation failed: Name has already been taken':
                # If the API key already exists, use it
                api_key = self._api_key_manager.get(name)
                if name == gen_name:
                    # For auto-generated API key, check its grants for the tables
                    granted_tables = list(map(lambda x: x.name, api_key.grants.tables))
                    if not granted_tables or any(table not in granted_tables for table in tables_names):
                        # If the API key does not grant all the tables (broken API key),
                        # delete it and create a new one with the same name
                        api_key.delete()
                        api_key = self._api_key_manager.create(name, apis, tables)
            else:
                raise e

        return api_key.name, api_key.token, tables_names


def _get_table_dict(schema, name, permissions):
    return {
        'schema': schema,
        'name': name,
        'permissions': permissions
    }


def _get_api_key_manager(credentials):
    auth_client = credentials.get_api_key_auth_client()
    return APIKeyManager(auth_client)

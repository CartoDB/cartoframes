from copy import deepcopy
from warnings import warn

from carto.kuvizs import KuvizManager
from carto.auth import APIKeyAuthClient

from .source import Source
from ..data.columns import normalize_name
from ..__version__ import __version__

from warnings import filterwarnings
filterwarnings("ignore", category=FutureWarning, module="carto")


class KuvizPublisher(object):
    def __init__(self, layers):
        self._layers = deepcopy(layers)

    @staticmethod
    def all(credentials=None):
        from ..auth import _default_credentials
        auth_client = _create_auth_client(credentials or _default_credentials)
        km = _get_kuviz_manager(auth_client)
        kuvizs = km.all()
        return [kuviz_to_dict(kuviz) for kuviz in kuvizs]

    def set_credentials(self, credentials=None):
        from ..auth import _default_credentials
        self._credentials = credentials or _default_credentials
        self._auth_client = _create_auth_client(self._credentials)

    def publish(self, html, name, password=None):
        return _create_kuviz(html=html, name=name, auth_client=self._auth_client, password=password)

    def is_sync(self):
        return all(layer.source.dataset.is_saved_in_carto for layer in self._layers)

    def is_public(self):
        return all(layer.source.dataset.is_public() for layer in self._layers)

    def get_layers(self, maps_api_key='default_public'):
        for layer in self._layers:
            layer.source.dataset.credentials = self._credentials

            layer.credentials = {
                'username': self._credentials.username,
                'api_key': maps_api_key,
                'base_url': self._credentials.base_url
            }

        return self._layers

    def sync_layers(self, table_name, credentials=None):
        for idx, layer in enumerate(self._layers):
            table_name = normalize_name("{name}_{idx}".format(name=table_name, idx=idx + 1))

            from ..auth import _default_credentials
            dataset_credentials = credentials or layer.source.dataset.credentials or _default_credentials

            self._sync_layer(layer, table_name, dataset_credentials)

    def _sync_layer(self, layer, table_name, credentials):
        if not layer.source.dataset.is_saved_in_carto:
            layer.source.dataset.upload(table_name=table_name, credentials=credentials)
            layer.source = Source(table_name, credentials=credentials)
            warn('Table `{}` created. In order to publish the map, you will need to create a new Regular API '
                 'key with permissions to Maps API and the table `{}`. You can do it from your CARTO dashboard or '
                 'using the Auth API. You can get more info at '
                 'https://carto.com/developers/auth-api/guides/types-of-API-Keys/'.format(table_name, table_name))


def _create_kuviz(html, name, auth_client, password=None):
    km = _get_kuviz_manager(auth_client)
    return km.create(html=html, name=name, password=password)


def _create_auth_client(credentials):
    return APIKeyAuthClient(
        base_url=credentials.base_url,
        api_key=credentials.api_key,
        session=credentials.session,
        client_id='cartoframes_{}'.format(__version__),
        user_agent='cartoframes_{}'.format(__version__)
    )


def _get_kuviz_manager(auth_client):
    return KuvizManager(auth_client)


def kuviz_to_dict(kuviz):
    return {'id': kuviz.id, 'url': kuviz.url, 'name': kuviz.name, 'privacy': kuviz.privacy}

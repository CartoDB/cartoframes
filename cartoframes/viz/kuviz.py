from copy import deepcopy
from warnings import warn

from carto.kuvizs import KuvizManager
from carto.exceptions import CartoException

from .source import Source
from ..columns import normalize_name

PRIVACY_PUBLIC = 'public'
PRIVACY_PASSWORD = 'password'


class KuvizPublisher(object):
    def __init__(self, vmap, context=None):
        self._layers = deepcopy(vmap.layers)
        self._context = context

    @staticmethod
    def all(context=None):
        km = _get_kuviz_manager(context)
        return km.all()

    def set_context(self, context=None):
        from ..auth import _default_context
        self._context = context or _default_context

    def publish(self, html, name, password=None):
        return _create_carto_kuviz(html=html, name=name, context=self._context, password=password)

    def is_sync(self):
        return all(layer.source.dataset.is_saved_in_carto for layer in self._layers)

    def is_public(self):
        return all(layer.source.dataset.is_public() for layer in self._layers)

    def get_layers(self, maps_api_key='default_public'):
        for layer in self._layers:
            layer.source.dataset.context = self._context

            layer.source.credentials = {
                'username': self._context.creds.username(),
                'api_key': maps_api_key,
                'base_url': self._context.creds.base_url()
            }

        return self._layers

    def sync_layers(self, table_name, context=None):
        for idx, layer in enumerate(self._layers):
            table_name = normalize_name("{name}_{idx}".format(name=table_name, idx=idx + 1))

            from ..auth import _default_context
            dataset_context = context or layer.source.dataset.context or _default_context

            self._sync_layer(layer, table_name, dataset_context)

    def _sync_layer(self, layer, table_name, context):
        if not layer.source.dataset.is_saved_in_carto:
            layer.source.dataset.upload(table_name=table_name, context=context)
            layer.source = Source(table_name, context=context)
            warn('Table `{}` created. In order to publish the map, you will need to create a new Regular API '
                 'key with permissions to Maps API and the table `{}`. You can do it from your CARTO dashboard or '
                 'using the Auth API. You can get more info at '
                 'https://carto.com/developers/auth-api/guides/types-of-API-Keys/'.format(table_name, table_name))


def _create_carto_kuviz(html, name, context=None, password=None):
    km = _get_kuviz_manager(context)
    carto_kuviz = km.create(html=html, name=name, password=password)

    _validate_carto_kuviz(carto_kuviz)

    return carto_kuviz


# FIXME: https://github.com/CartoDB/carto-python/issues/122
# Remove the function and usage after the issue will be fixed
def _validate_carto_kuviz(carto_kuviz):
    if not carto_kuviz or not carto_kuviz.url or not carto_kuviz.id or not carto_kuviz.name:
        raise CartoException('Error creating Kuviz. Something goes wrong')

    if carto_kuviz.privacy and carto_kuviz.privacy not in [PRIVACY_PUBLIC, PRIVACY_PASSWORD]:
        raise CartoException('Error creating Kuviz. Invalid privacy')

    return True


def _get_kuviz_manager(context=None):
    from cartoframes.auth import _default_context
    context = context or _default_context

    return KuvizManager(context.auth_client)

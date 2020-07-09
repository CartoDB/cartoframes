import copy

from warnings import filterwarnings
from carto.kuvizs import KuvizManager

from ..data.clients.auth_api_client import AuthAPIClient
from ..exceptions import PublishError
from ..utils.logger import log
from ..utils.utils import get_credentials

filterwarnings('ignore', category=FutureWarning, module='carto')

DEFAULT_PUBLIC = 'default_public'


class KuvizPublisher:
    def __init__(self, credentials=None):
        self.kuviz = None
        self._layers = []
        self._auth_client = _create_auth_client(credentials)
        self._auth_api_client = _create_auth_api_client(credentials)

    def get_layers(self):
        return self._layers

    def set_layers(self, layers, maps_api_key=None):
        new_maps_api_key = None
        if maps_api_key is None:
            new_maps_api_key = self._create_maps_api_keys(layers)

        self._layers = []
        for layer in layers:
            layer_copy = copy.deepcopy(layer)

            if layer_copy.credentials is not None:
                if layer_copy.source.is_public():
                    layer_copy.credentials['api_key'] = maps_api_key or DEFAULT_PUBLIC
                else:
                    layer_copy.credentials['api_key'] = maps_api_key or new_maps_api_key

            self._layers.append(layer_copy)

    def publish(self, html, name, password, if_exists='fail'):
        self.kuviz = _create_kuviz(html, name, self._auth_client, password, if_exists)
        return kuviz_to_dict(self.kuviz)

    def update(self, data, name, password, if_exists='fail'):
        if not self.kuviz:
            raise PublishError('The map has not been published yet. Use the `publish` method instead.')

        self.kuviz.data = data
        self.kuviz.name = name
        self.kuviz.password = password
        self.kuviz.if_exists = if_exists

        try:
            self.kuviz.save()
        except Exception as e:
            manage_kuviz_exception(e, name)

        return kuviz_to_dict(self.kuviz)

    def delete(self):
        if self.kuviz:
            self.kuviz.delete()
            log.warning("Publication '{n}' ({id}) deleted".format(n=self.kuviz.name, id=self.kuviz.id))
            self.kuviz = None
            return True
        return False

    def _create_maps_api_keys(self, layers):
        private_sources = [layer.source for layer in layers if not layer.source.is_public()]

        if len(private_sources) > 0:
            key_name, key_value, private_tables_names = self._auth_api_client.create_api_key(
                private_sources, ['maps']
            )
            log.info(
                'The map has been published. '
                'The "{0}" Maps API key with value "{1}" is being used for the datasets: {2}. '
                'You can manage your API keys on your account.'.format(
                    key_name, key_value, ', '.join(['"{}"'.format(name) for name in private_tables_names])))
            return key_value

        return DEFAULT_PUBLIC


def _create_kuviz(html, name, auth_client, password, if_exists):
    kmanager = _get_kuviz_manager(auth_client)

    try:
        return kmanager.create(html=html, name=name, password=password, if_exists=if_exists)
    except Exception as e:
        manage_kuviz_exception(e, name)


def _create_auth_client(credentials):
    return credentials.get_api_key_auth_client()


def _create_auth_api_client(credentials):
    return AuthAPIClient(credentials)


def _get_kuviz_manager(auth_client):
    return KuvizManager(auth_client)


def kuviz_to_dict(kuviz):
    return {
        'id': kuviz.id,
        'url': kuviz.url,
        'name': kuviz.name,
        'privacy': kuviz.privacy
    }


def manage_kuviz_exception(error, name):
    if str(error) == 'Validation failed: Name has already been taken':
        raise PublishError("Map '{}' already exists in your CARTO account. Please, choose a different `name` "
                           "or use if_exists='replace' to overwrite it.".format(name))

    if str(error) == 'Visualization over the size limit (10MB)':
        raise PublishError("Map '{}' exceeds the size limit of 10MB. Please, upload your data to CARTO calling "
                           "to_carto() function and use the table names in the layers instead.".format(name))

    if str(error) == 'Public map quota exceeded':
        raise PublishError("You have reached the limit for the number of maps you can create with your account. "
                           "Upgrade your account or delete some of your previous maps to be able to create new ones.")

    raise error


def all_publications(credentials=None):
    """Get all map visualizations published by the current user.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. If not provided, the credentials will be automatically
            obtained from the default credentials if available.

    """
    _credentials = get_credentials(credentials)
    auth_client = _create_auth_client(_credentials)
    kmanager = _get_kuviz_manager(auth_client)
    kuvizs = kmanager.all()
    return [kuviz_to_dict(kuviz) for kuviz in kuvizs]


def delete_publication(name, credentials=None):
    """Delete a map visualization published by id.

    Args:
        name (str): name of the publication to be deleted.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. If not provided, the credentials will be automatically
            obtained from the default credentials if available.

    """
    _credentials = get_credentials(credentials)
    auth_client = _create_auth_client(_credentials)
    kmanager = _get_kuviz_manager(auth_client)
    kuvizs = kmanager.all()
    kuviz = next((kuviz for kuviz in kuvizs if kuviz.name == name), None)

    if kuviz is None:
        raise PublishError('Publication "{}" not found.'.format(name))

    try:
        kuviz.delete()
        log.info('Success! Publication "{0}" deleted'.format(name))
    except Exception as e:
        manage_kuviz_exception(e, name)

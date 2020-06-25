import copy

from carto.kuvizs import Kuviz
from cartoframes.viz.kuviz import KuvizPublisher, kuviz_to_dict

PRIVACY_PUBLIC = 'public'
PRIVACY_PASSWORD = 'password'


class CartoKuvizMock(Kuviz):
    def __init__(self, name, id='a12345', url='https://carto.com', password=None):
        self.id = id
        self.url = url
        self.name = name
        if password:
            self.privacy = PRIVACY_PASSWORD
        else:
            self.privacy = PRIVACY_PUBLIC

    def save(self):
        return True

    def delete(self):
        return True


class KuvizPublisherMock(KuvizPublisher):
    def __init__(self):
        self._layers = []

    def get_layers(self):
        return self._layers

    def set_layers(self, layers, maps_api_key):
        if maps_api_key:
            layers_copy = []
            for layer in layers:
                layer_copy = copy.deepcopy(layer)
                layer_copy.credentials['api_key'] = maps_api_key
                layers_copy.append(layer_copy)
            layers = layers_copy
        self._layers = layers

    def publish(self, html, name, password, if_exists='fail'):
        self.kuviz = CartoKuvizMock(name, password=password)
        return kuviz_to_dict(self.kuviz)

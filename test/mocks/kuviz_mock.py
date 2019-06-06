from cartoframes.viz.kuviz import KuvizPublisher, PRIVACY_PUBLIC, PRIVACY_PASSWORD, _validate_carto_kuviz


class CartoKuvizMock(object):
    def __init__(self, name, id='a12345', url="https://carto.com", password=None):
        self.id = id
        self.url = url
        self.name = name
        if password:
            self.privacy = PRIVACY_PASSWORD
        else:
            self.privacy = PRIVACY_PUBLIC


def _create_carto_kuviz(html, name, context=None, password=None):
    carto_kuviz = CartoKuvizMock(name=name, password=password)
    _validate_carto_kuviz(carto_kuviz)
    return carto_kuviz


class KuvizPublisherMock(KuvizPublisher):
    def publish(self, html, name, password=None):
        return _create_carto_kuviz(html=html, name=name, context=self._context, password=password)

    def _sync_layer(self, layer, table_name, context):
        layer.source.dataset._is_saved_in_carto = True

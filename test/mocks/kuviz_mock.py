from cartoframes.viz.kuviz import Kuviz, _validate_carto_kuviz, KuvizPublisher


class CartoKuvizMock(object):
    def __init__(self, name, id='a12345', url="https://carto.com", password=None):
        self.id = id
        self.url = url
        self.name = name
        if password:
            self.privacy = Kuviz.PRIVACY_PASSWORD
        else:
            self.privacy = Kuviz.PRIVACY_PUBLIC


class KuvizMock(Kuviz):
    @classmethod
    def create(cls, context, html, name, password=None):
        carto_kuviz = _create_carto_kuviz(context, html, name, password)
        _validate_carto_kuviz(carto_kuviz)
        return cls(context, carto_kuviz.id, carto_kuviz.url, carto_kuviz.name, carto_kuviz.privacy)


def _create_carto_kuviz(context, html, name, password=None):
    return CartoKuvizMock(name=name, password=password)


class KuvizPublisherMock(KuvizPublisher):
    def publish(self, html, name, password=None):
        return KuvizMock.create(context=self._context, html=html, name=name, password=password)

    def _sync_layer(self, layer, table_name, context):
        layer.source.dataset._is_saved_in_carto = True

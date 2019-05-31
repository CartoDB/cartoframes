from cartoframes.viz.kuviz import Kuviz


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
    def _create_carto_kuviz(self, context, html, name, password=None):
        return CartoKuvizMock(name=name, password=password)

from carto.kuvizs import KuvizManager
from carto.exceptions import CartoException


class Kuviz(object):
    PRIVACY_PUBLIC = 'public'
    PRIVACY_PASSWORD = 'password'

    def __init__(self, context, id, url, name, privacy=PRIVACY_PUBLIC):
        self.cc = context
        self.id = id
        self.url = url
        self.name = name
        self.privacy = privacy

    @classmethod
    def create(cls, context, html, name, password=None):
        carto_kuviz = _create_carto_kuviz(context, html, name, password)
        _validate_carto_kuviz(carto_kuviz)
        return cls(context, carto_kuviz.id, carto_kuviz.url, carto_kuviz.name, carto_kuviz.privacy)

    @classmethod
    def all(cls, context):
        # km = KuvizManager(context.auth_client)
        # return km.all()
        pass

    def update(self, html, name, password=None):
        pass

    def delete(self):
        pass


# FIXME: https://github.com/CartoDB/carto-python/issues/122
# Remove the function and usage after the issue will be fixed
def _validate_carto_kuviz(carto_kuviz):
    if not carto_kuviz or not carto_kuviz.url or not carto_kuviz.id or not carto_kuviz.name:
        raise CartoException('Error creating Kuviz. Something goes wrong')

    if carto_kuviz.privacy and carto_kuviz.privacy not in [Kuviz.PRIVACY_PUBLIC, Kuviz.PRIVACY_PASSWORD]:
        raise CartoException('Error creating Kuviz. Invalid privacy')

    return True


def _create_carto_kuviz(context, html, name, password=None):
    km = KuvizManager(context.auth_client)
    return km.create(html=html, name=name, password=password)

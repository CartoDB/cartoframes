from carto.kuvizs import Kuviz

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

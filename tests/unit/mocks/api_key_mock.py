from cartoframes.utils.utils import create_hash


class APIKeyMock():
    def __init__(self, name, token):
        self.name = name
        self.token = token
        self.type = None
        self.created_at = None
        self.updated_at = None
        self.grants = None


class APIKeyManagerMock():
    def __init__(self, token=''):
        self.token = token

    def create(self, name, apis, tables):
        return APIKeyMock(name, self.token)


class Grants:
    def __init__(self):
        self.tables = []


class APIKey():
    def __init__(self):
        self.grants = Grants()


class APIKeyManagerFailureMock():
    def __init__(self, token=''):
        self.token = token

    def create(self, name, apis, tables):
        if(name == 'cartoframes_{}'.format(create_hash(['fake_table']))):
            raise Exception('Validation failed: Name has already been taken')
        else:
            return APIKeyMock(name, self.token)

    def get(self, name):
        api_key = APIKey()
        return api_key

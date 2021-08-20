class TableMock():
    def __init__(self, name):
        self.name = name


class GrantsMock():
    def __init__(self, tables):
        self.tables = [TableMock(table) for table in tables]


class APIKeyMock():
    def __init__(self, name, token, tables):
        self.name = name
        self.token = token
        self.type = None
        self.created_at = None
        self.updated_at = None
        self.grants = GrantsMock(tables)
        self.exists = True

    def delete(self):
        self.exists = False


class APIKeyManagerMock():
    def __init__(self, token=''):
        self.token = token
        self.api_keys = {}

    def create(self, name, apis, tables):
        if name in self.api_keys and self.api_keys[name].exists:
            raise Exception('Validation failed: Name has already been taken')
        self.api_keys[name] = APIKeyMock(name, self.token, tables)
        return self.api_keys[name]

    def get(self, name):
        return self.api_keys[name]

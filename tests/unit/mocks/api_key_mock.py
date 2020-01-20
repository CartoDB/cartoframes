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

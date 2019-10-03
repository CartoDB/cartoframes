
class ContextMock():
    def __init__(self):
        self.query = None
        self.response = None

    def upload(self, query, data):
        self.query = query
        self.response = data

    def execute_query(self, query, **kwargs):
        self.query = query
        return self.response

    def execute_long_running_query(self, query):
        self.query = query
        return self.response

    def get_schema(self):
        return 'public'

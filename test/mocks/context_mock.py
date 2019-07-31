
class ContextMock():
    def __init__(self):
        self.query = ''
        self.response = ''

    def execute_query(self, q, **kwargs):
        self.query = q
        return self.response

    def execute_long_running_query(self, q):
        self.query = q
        return self.response

    def get_schema(self):
        return 'public'

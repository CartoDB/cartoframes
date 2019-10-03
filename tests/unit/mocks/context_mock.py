class ContextMock():
    def __init__(self, response=''):
        self.query = None
        self.response = response

    def upload(self, query, data):
        self.query = query
        self.response = data

    def execute_query(self, query, do_post=None):
        self.query = query
        return self.response

    def execute_long_running_query(self, query):
        self.query = query
        return self.response

    def get_schema(self):
        return 'public'

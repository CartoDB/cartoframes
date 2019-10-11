class BigQueryClientMock(object):
    def __init__(self, response):
        self.response = response

    def download_to_file(self, _1, _2, _3):
        if isinstance(self.response, Exception):
            raise self.response
        else:
            return self.response


class CredentialsMock(object):
    def __init__(self, username):
        self.username = username

    def get_do_dataset(self):
        return self.username.replace('-', '_')

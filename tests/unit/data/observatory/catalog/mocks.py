class BigQueryClientMock(object):
    def __init__(self, response):
        self.response = response

        self.bucket_name = 'bucket_name'
        self.public_data_project = 'public_data_project'
        self.user_data_project = 'user_data_project'
        self.dataset = 'username'
        self.bucket_name = 'bucket_name'

    def download_to_file(self, _1, _2, _3, _4):
        if isinstance(self.response, Exception):
            raise self.response
        else:
            return self.response

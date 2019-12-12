class BigQueryClientMock(object):
    def __init__(self, response):
        self.response = response

        self.bq_public_project = 'public_data_project'
        self.bq_project = 'user_data_project'
        self.bq_dataset = 'username'
        self._gcs_bucket = 'bucket_name'

    def download_to_file(self, _1, _2, _3, _4):
        if isinstance(self.response, Exception):
            raise self.response
        else:
            return self.response

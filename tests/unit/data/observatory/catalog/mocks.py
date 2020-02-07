from urllib.parse import urlsplit, parse_qsl
from .examples import db_dataset1, db_dataset2


class BigQueryClientMock(object):
    def __init__(self, exception=None):
        self.exception = exception

        self.bq_public_project = 'public_data_project'
        self.bq_project = 'user_data_project'
        self.bq_dataset = 'username'
        self._gcs_bucket = 'bucket_name'

    def query(self, _1):
        return True

    def download_to_file(self, _1, _2, column_names=None):
        if isinstance(self.exception, Exception):
            raise self.exception

    def get_table_column_names(self, _1, _2, _3):
        return True


class MockReponse:

    def __init__(self, json_data=None):
        self.json_data = json_data

    def json(self):
        return self.json_data


def mocked_do_api_requests_get_datasets(request_url, *args, **kwargs):
    # Just returns original filters dict
    url = urlsplit(request_url)
    orig_filters = dict(parse_qsl(url.query))

    if url.path.endswith('/metadata/datasets'):
        # Case for test filters:
        return MockReponse(json_data=orig_filters)
    else:
        # Testing requests by id/slug
        # The last part of the url path should be the dataset_id
        dataset_id = url.path.split('/')[-1]
        if dataset_id in [db_dataset1['id'], db_dataset1['slug']]:
            return MockReponse(json_data=db_dataset1)
        elif dataset_id in [db_dataset2['id'], db_dataset2['slug']]:
            return MockReponse(json_data=db_dataset2)
        else:
            return MockReponse()

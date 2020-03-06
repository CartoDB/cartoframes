import os
import time
import requests
from carto.utils import ResponseStream
from carto.exceptions import CartoException
from ...auth import get_default_credentials

VALID_TYPES = [
    'STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT',
    'FLOAT64', 'BOOLEAN', 'BOOL', 'TIMESTAMP', 'DATE', 'TIME',
    'DATETIME', 'GEOMETRY'
]

TYPES_MAPPING = {
    'GEOMETRY': 'GEOGRAPHY'
}

API_BASE_PATH = 'api/v4/data/observatory'
DATASETS_BASE_PATH = 'bq/datasets'
ENRICHMENT_BASE_PATH = 'bq/enrichment'


def _build_api_url(base_url, resource):
    return '{}/{}/{}'.format(base_url, API_BASE_PATH, resource)


class _BQDatasetClient:

    def __init__(self, credentials):
        self.session = requests.Session()
        self._credentials = credentials
        self._username = credentials.username
        self._api_key = credentials.api_key
        self._base_url = credentials.base_url.format(self._username)

    def upload(self, dataframe, name, params=None):
        params = params or {}
        dataframe.to_csv(path_or_buf=name, index=False)
        try:
            with open(name, 'rb') as f:
                self.upload_file_object(f, name, params)
        finally:
            os.remove(name)

    def upload_file_object(self, file_object, name, params=None):
        params = params or {}
        upload_file_path = '{}/{}'.format(DATASETS_BASE_PATH, name)
        url = _build_api_url(self._base_url, upload_file_path)
        params['api_key'] = self._api_key

        try:
            response = self.session.post(url, params=params, data=file_object)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def import_dataset(self, name):
        import_dataset_path = '{}/{}/imports'.format(DATASETS_BASE_PATH, name)
        url = _build_api_url(self._base_url, import_dataset_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()

            job = response.json()

            return BQJob(job['item_queue_id'], name, self._credentials)
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def upload_dataframe(self, dataframe, name, params=None):
        params = params or {}
        self.upload(dataframe, name, params)
        job = self.import_dataset(name)
        status = job.result()

        return status

    def download(self, name_id):
        download_path = '{}/{}'.format(DATASETS_BASE_PATH, name_id)
        url = _build_api_url(self._base_url, download_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.get(url, params=params, stream=True)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def download_stream(self, name_id):
        return ResponseStream(self.download(name_id))

    def create(self, payload):
        create_path = DATASETS_BASE_PATH
        url = _build_api_url(self._base_url, create_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            else:
                raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def enrichment(self, payload):
        enrichment_path = ENRICHMENT_BASE_PATH
        url = _build_api_url(self._base_url, enrichment_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()

            body = response.json()
            job = BQUserEnrichmentJob(body['job_id'], self._credentials)
            status = job.result()

            return status
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)


class BQJob:

    def __init__(self, job_id, name_id, credentials):
        self.id = job_id
        self.name = name_id
        self._username = credentials.username
        self._api_key = credentials.api_key
        self._base_url = credentials.base_url
        self.session = requests.Session()

    def status(self):
        status_path = '{}/{}/imports/{}'.format(DATASETS_BASE_PATH, self.name, self.id)
        url = _build_api_url(self._base_url, status_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            body = response.json()

            if body['status'] == 'failure':
                msg = u'Client Error: %s' % (body['errors'][0])
                raise CartoException(msg)

            return body['status']
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def result(self):
        status = self.status()

        while status not in ('success', 'failure'):
            time.sleep(1)
            status = self.status()

        return status


class BQUserEnrichmentJob:

    def __init__(self, job_id, credentials):
        self.id = job_id
        self._username = credentials.username
        self._api_key = credentials.api_key
        self._base_url = credentials.base_url
        self.session = requests.Session()

    def status(self):
        status_path = '{}/{}/status'.format(ENRICHMENT_BASE_PATH, self.id)
        url = _build_api_url(self._base_url, status_path)
        params = {'api_key': self._api_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            body = response.json()

            if body['status'] == 'failure':
                msg = u'Client Error: %s' % (body['errors'][0])
                raise CartoException(msg)

            return body['status']
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def result(self):
        status = self.status()

        while status not in ('success', 'failure'):
            time.sleep(1)
            status = self.status()

        return status


class BQUserDataset:

    @staticmethod
    def _map_type(in_type):
        if in_type in TYPES_MAPPING:
            out_type = TYPES_MAPPING[in_type]
        else:
            out_type = in_type
        return out_type

    def __init__(self, name=None, columns=None, ttl_seconds=None, client=None, credentials=None):
        self._name = name
        if columns is None:
            self._columns = []
        else:
            self._columns = columns
        self._ttl_seconds = ttl_seconds
        self._client = client
        if self._client is None:
            self._credentials = credentials or get_default_credentials()
            self._client = _BQDatasetClient(self._credentials)

    def name(self, name):
        self._name = name
        return self

    def column(self, name=None, type=None):
        # TODO validate field names
        type = type.upper()
        if type not in VALID_TYPES:
            # TODO custom exception
            raise Exception('Invalid type %s' % type)
        self._columns.append((name, type))
        return self

    def ttl_seconds(self, ttl_seconds):
        self._ttl_seconds = ttl_seconds
        return self

    def create(self):
        payload = {
            'id': self._name,
            'schema': [{'name': c[0], 'type': self._map_type(c[1])} for c in self._columns],
        }
        if self._ttl_seconds is not None:
            payload['ttl_seconds'] = self._ttl_seconds
        self._client.create(payload)

    def download_stream(self):
        return self._client.download_stream(self._name)

    def upload(self, dataframe):
        self._client.upload(dataframe, self._name)

    def upload_file_object(self, file_object):
        self._client.upload_file_object(file_object, self._name)

    def import_dataset(self):
        return self._client.import_dataset(self._name)

    def upload_dataframe(self, dataframe, geom_column=None):
        return self._client.upload_dataframe(dataframe, self._name, params={'geom_column': geom_column})

    def enrichment(self, geom_type='points', variables=None, filters=None, aggregation=None, output_name=None):
        payload = {
            'type': geom_type,
            'input': self._name,
            'variables': variables,
            'filters': filters,
            'aggregation': aggregation,
            'output': output_name
        }

        return self._client.enrichment(payload)

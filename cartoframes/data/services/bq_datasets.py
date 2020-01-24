import os
import requests
from carto.utils import ResponseStream
# from carto.auth import APIKeyAuthClient

from carto.exceptions import CartoException

# TODO: this shouldn't be hardcoded
DO_ENRICHMENT_API_URL = 'http://localhost:7070/bq'

VALID_TYPES = [
    'STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT',
    'FLOAT64', 'BOOLEAN', 'BOOL', 'TIMESTAMP', 'DATE', 'TIME',
    'DATETIME', 'GEOMETRY'
]

TYPES_MAPPING = {
    'GEOMETRY': 'GEOGRAPHY'
}


class _BQDatasetClient:

    def __init__(self):
        # TODO fix this crap
        self.session = requests.Session()
        self.api_key = 'my_valid_api_key'

    def upload(self, dataframe, name):
        dataframe.to_csv(path_or_buf=name, index=False)
        try:
            with open(name, 'rb') as f:
                self.upload_file_object(f, name)
        finally:
            os.remove(name)

    def upload_file_object(self, file_object, name):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + name
        params = {'api_key': self.api_key}

        try:
            response = self.session.post(url, params=params, data=file_object)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def import_dataset(self, name):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + name + '/imports'
        params = {'api_key': self.api_key}

        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()

            job = response.json()

            return BQJob(job['item_queue_id'], name)
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def upload_dataframe(self, dataframe, name):
        self.upload(dataframe, name)
        job = self.import_dataset(name)
        status = job.result()

        return status

    def download(self, name_id):
        url = '%s/datasets/%s' % (DO_ENRICHMENT_API_URL, name_id)
        params = {'api_key': self.api_key}

        try:
            response = self.session.get(url,
                                        params=params,
                                        stream=True)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['error'][0]
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
        url = '%s/datasets' % DO_ENRICHMENT_API_URL
        params = {'api_key': self.api_key}

        try:
            response = self.session.post(url,
                                         params=params,
                                         json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            else:
                raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response


class BQJob:

    def __init__(self, job_id, name_id):
        self.id = job_id
        self.name = name_id
        # TODO fix this crap
        self.session = requests.Session()
        self.api_key = 'my_valid_api_key'

    def status(self):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + self.name + '/imports/' + self.id
        params = {'api_key': self.api_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            body = response.json()

            return body['status']
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def result(self):
        status = self.status()

        while status != 'done' and status != 'failed':
            status = self.status()

        return status


class BQUserDataset:

    @staticmethod
    def name(name_id):
        return BQUserDataset(name_id)

    @staticmethod
    def _map_type(in_type):
        if in_type in TYPES_MAPPING:
            out_type = TYPES_MAPPING[in_type]
        else:
            out_type = in_type
        return out_type

    def __init__(self, name_id, client=None, ttl_seconds=None):
        self._name_id = name_id
        if client is None:
            self._client = _BQDatasetClient()
        self._columns = []
        self._ttl_seconds = ttl_seconds

    def download_stream(self):
        return self._client.download_stream(self._name_id)

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
            'id': self._name_id,
            'schema': [{'name': c[0], 'type': self._map_type(c[1])} for c in self._columns],
        }
        if self._ttl_seconds is not None:
            payload['ttl_seconds'] = self._ttl_seconds
        self._client.create(payload)

    def upload(self, dataframe):
        self._client.upload(dataframe, self._name_id)

    def upload_file_object(self, file_object):
        self._client.upload_file_object(file_object, self._name_id)

    def import_dataset(self):
        return self._client.import_dataset(self._name_id)

    def upload_dataframe(self, dataframe):
        return self._client.upload_dataframe(dataframe, self._name_id)

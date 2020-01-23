import os
import requests
from carto.utils import ResponseStream
# from carto.auth import APIKeyAuthClient

from carto.exceptions import CartoException

# TODO: this shouldn't be hardcoded
DO_ENRICHMENT_API_URL = 'http://localhost:7070/bq'


class BQDataset:

    def __init__(self, name_id):
        self.name = name_id
        # TODO fix this crap
        self.session = requests.Session()
        self.api_key = 'my_valid_api_key'

    def upload(self, dataframe):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + self.name
        params = {'api_key': self.api_key}

        try:
            dataframe.to_csv(self.name, index=False)

            with open(self.name, 'rb') as f:
                response = self.session.post(url, params=params, data=f)
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
        finally:
            os.remove(self.name)

    def upload_file_object(self, file_object):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + self.name
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

    def import_dataset(self):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + self.name + '/imports'
        params = {'api_key': self.api_key}

        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()

            job = response.json()

            return BQJob(job['item_queue_id'], self.name)
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code,
                                                      reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def upload_dataframe(self, dataframe):
        # missing call to create the dataset
        self.upload(dataframe)
        job = self.import_dataset()
        status = job.result()

        return status

    def download(self):
        url = DO_ENRICHMENT_API_URL + '/datasets/' + self.name
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

    def download_stream(self):
        return ResponseStream(self.download())


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

        while status != 'done':
            status = self.status()

        return status


class BQUserDataset:

    @staticmethod
    def name(name_id):
        return BQDataset(name_id)

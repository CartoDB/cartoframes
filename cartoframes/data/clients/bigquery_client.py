from __future__ import absolute_import

import os
import appdirs
import csv
import tqdm

from google.auth.exceptions import RefreshError
from google.cloud import bigquery, storage
from google.oauth2.credentials import Credentials as GoogleCredentials

from carto.exceptions import CartoException
from ...auth import get_default_credentials

_USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')
_GCS_CHUNK_SIZE = 25 * 1024 * 1024  # 25MB. This must be a multiple of 256 KB per the API specification.


def refresh_clients(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RefreshError:
            self._init_clients()
            try:
                return func(self, *args, **kwargs)
            except RefreshError:
                raise CartoException('Something went wrong accessing data. '
                                     'Please, try again in a few seconds or contact support for help.')
    return wrapper


class BigQueryClient(object):

    def __init__(self, credentials):
        self._credentials = credentials or get_default_credentials()
        self.bq_client = None
        self.gcs_client = None

        self.bq_public_project = None
        self.bq_project = None
        self.bq_dataset = None
        self.instant_licensing = None
        self._gcs_bucket = None

        self._init_clients()

    def _init_clients(self):
        do_credentials = self._credentials.get_do_credentials()
        google_credentials = GoogleCredentials(do_credentials.access_token)

        self.bq_client = bigquery.Client(
            project=do_credentials.gcp_execution_project,
            credentials=google_credentials)

        self.gcs_client = storage.Client(
            project=do_credentials.bq_project,
            credentials=google_credentials
        )

        self.bq_public_project = do_credentials.bq_public_project
        self.bq_project = do_credentials.bq_project
        self.bq_dataset = do_credentials.bq_dataset
        self.instant_licensing = do_credentials.instant_licensing
        self._gcs_bucket = do_credentials.gcs_bucket

    @refresh_clients
    def upload_dataframe(self, dataframe, schema, tablename):
        # Upload file to Google Cloud Storage
        bucket = self.gcs_client.get_bucket(self._gcs_bucket)
        blob = bucket.blob(tablename, chunk_size=_GCS_CHUNK_SIZE)
        dataframe.to_csv(tablename, index=False, header=False)
        try:
            blob.upload_from_filename(tablename)
        finally:
            os.remove(tablename)

        # Import from GCS To BigQuery
        dataset_ref = self.bq_client.dataset(self.bq_dataset, project=self.bq_project)
        table_ref = dataset_ref.table(tablename)
        schema_wrapped = [bigquery.SchemaField(column, dtype) for column, dtype in schema.items()]

        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema_wrapped
        job_config.source_format = bigquery.SourceFormat.CSV
        uri = 'gs://{bucket}/{tablename}'.format(bucket=self._gcs_bucket, tablename=tablename)

        job = self.bq_client.load_table_from_uri(
            uri, table_ref, job_config=job_config
        )

        job.result()  # Waits for table load to complete.

    @refresh_clients
    def query(self, query, **kwargs):
        return self.bq_client.query(query, **kwargs)

    @refresh_clients
    def get_table(self, project, dataset, table):
        full_table_name = '{}.{}.{}'.format(project, dataset, table)
        return self.bq_client.get_table(full_table_name)

    def get_table_column_names(self, project, dataset, table):
        table_info = self.get_table(project, dataset, table)
        return [field.name for field in table_info.schema]

    def download_to_file(self, project, dataset, table, file_path=None, limit=None, offset=None,
                         fail_if_exists=False, progress_bar=True):
        if not file_path:
            file_name = '{}.{}.{}.csv'.format(project, dataset, table)
            file_path = os.path.join(_USER_CONFIG_DIR, file_name)

        if fail_if_exists and os.path.isfile(file_path):
            raise CartoException('The file `{}` already exists.'.format(file_path))

        column_names = self.get_table_column_names(project, dataset, table)

        query = _download_query(project, dataset, table, limit, offset)
        rows_iter = self.query(query).result()

        if progress_bar:
            pb = tqdm.tqdm_notebook(total=rows_iter.total_rows)

        with open(file_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)

            csvwriter.writerow(column_names)

            for row in rows_iter:
                csvwriter.writerow(row.values())
                if progress_bar:
                    pb.update(1)

        return file_path


def _download_query(project, dataset, table, limit=None, offset=None):
    full_table_name = '`{}.{}.{}`'.format(project, dataset, table)
    query = 'SELECT * FROM {}'.format(full_table_name)

    if limit:
        query += ' LIMIT {}'.format(limit)
    if offset:
        query += ' OFFSET {}'.format(offset)

    return query

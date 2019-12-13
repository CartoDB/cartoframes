from __future__ import absolute_import

import os
import appdirs
import csv
import tqdm
import pandas as pd

from google.auth.exceptions import RefreshError
from google.cloud import bigquery, storage, bigquery_storage_v1beta1 as bigquery_storage
from google.oauth2.credentials import Credentials as GoogleCredentials

from carto.exceptions import CartoException
from ...auth import get_default_credentials
from ...core.logger import log
from ...utils.utils import timelogger


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
        self.bq_storage_client = None

        self._gcp_execution_project = None
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
            credentials=google_credentials
        )

        self.gcs_client = storage.Client(
            project=do_credentials.bq_project,
            credentials=google_credentials
        )

        self.bq_storage_client = bigquery_storage.BigQueryStorageClient(
            credentials=google_credentials
        )

        self._gcp_execution_project = do_credentials.gcp_execution_project
        self.bq_public_project = do_credentials.bq_public_project
        self.bq_project = do_credentials.bq_project
        self.bq_dataset = do_credentials.bq_dataset
        self.instant_licensing = do_credentials.instant_licensing
        self._gcs_bucket = do_credentials.gcs_bucket

    @refresh_clients
    def query(self, query, **kwargs):
        return self.bq_client.query(query, **kwargs)

    def upload_dataframe(self, dataframe, schema, tablename):
        self._upload_dataframe_to_GCS(dataframe, tablename)
        self._import_from_GCS_to_BQ(schema, tablename)

    @timelogger
    def download_to_file(self, job, file_path, fail_if_exists=False, column_names=None, progress_bar=True):
        if fail_if_exists and os.path.isfile(file_path):
            raise CartoException('The file `{}` already exists.'.format(file_path))

        try:
            rows = self._download_by_bq_storage_api(job)
        except Exception:
            log.debug('Cannot download using BigQuery Storage API, fallback to standard')
            rows = job.result()

        _rows_to_file(rows, file_path, column_names, progress_bar)

    @timelogger
    def download_to_dataframe(self, job):
        try:
            rows = self._download_by_bq_storage_api(job)
            data = list(rows)
            return pd.DataFrame(data)
        except Exception:
            log.debug('Cannot download using BigQuery Storage API, fallback to standard')
            return job.to_dataframe()

    def _download_by_bq_storage_api(self, job):
        table_ref = job.destination.to_bqstorage()

        parent = 'projects/{}'.format(self._gcp_execution_project)
        session = self.bq_storage_client.create_read_session(
            table_ref,
            parent,
            requested_streams=1,
            format_=bigquery_storage.enums.DataFormat.AVRO,
            # We use a LIQUID strategy because we only read from a
            # single stream. Consider BALANCED if requested_streams > 1
            sharding_strategy=(bigquery_storage.enums.ShardingStrategy.LIQUID)
        )

        reader = self.bq_storage_client.read_rows(
            bigquery_storage.types.StreamPosition(stream=session.streams[0])
        )

        return reader.rows(session)

    @refresh_clients
    @timelogger
    def _upload_dataframe_to_GCS(self, dataframe, tablename):
        log.debug('Uploading to GCS')
        bucket = self.gcs_client.get_bucket(self._gcs_bucket)
        blob = bucket.blob(tablename, chunk_size=_GCS_CHUNK_SIZE)
        dataframe.to_csv(tablename, index=False, header=False)
        try:
            blob.upload_from_filename(tablename)
        finally:
            os.remove(tablename)

    @refresh_clients
    @timelogger
    def _import_from_GCS_to_BQ(self, schema, tablename):
        log.debug('Importing to BQ from GCS')

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

    def get_table_column_names(self, project, dataset, table):
        table_info = self._get_table(project, dataset, table)
        return [field.name for field in table_info.schema]

    @refresh_clients
    def _get_table(self, project, dataset, table):
        full_table_name = '{}.{}.{}'.format(project, dataset, table)
        return self.bq_client.get_table(full_table_name)


def _rows_to_file(rows, file_path, column_names=None, progress_bar=True):
    if progress_bar:
        pb = tqdm.tqdm_notebook(total=rows.total_rows)

    with open(file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        if column_names:
            csvwriter.writerow(column_names)

        for row in rows:
            csvwriter.writerow(row.values())
            if progress_bar:
                pb.update(1)

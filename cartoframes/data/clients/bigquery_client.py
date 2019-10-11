from __future__ import absolute_import

import os
import appdirs
import csv
import tqdm

from google.cloud import bigquery
from google.oauth2.credentials import Credentials as GoogleCredentials
from google.auth.exceptions import RefreshError

from carto.exceptions import CartoException

from ...auth import get_default_credentials

_USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')


def refresh_client(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RefreshError:
            self.client = self._init_client()
            try:
                return func(self, *args, **kwargs)
            except RefreshError:
                raise CartoException('Something went wrong accessing data. '
                                     'Please, try again in a few seconds or contact support for help.')
    return wrapper


class BigQueryClient(object):

    def __init__(self, project, credentials):
        self._project = project
        self._credentials = credentials or get_default_credentials()
        self.client = self._init_client()

    def _init_client(self):
        google_credentials = GoogleCredentials(self._credentials.get_do_token())

        return bigquery.Client(
            project=self._project,
            credentials=google_credentials)

    @refresh_client
    def upload_dataframe(self, dataframe, schema, tablename, project, dataset):
        dataset_ref = self.client.dataset(dataset, project=project)
        table_ref = dataset_ref.table(tablename)

        schema_wrapped = [bigquery.SchemaField(column, dtype) for column, dtype in schema.items()]

        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema_wrapped

        job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
        job.result()

    @refresh_client
    def query(self, query, **kwargs):
        return self.client.query(query, **kwargs)

    @refresh_client
    def get_table(self, project, dataset, table):
        full_table_name = '{}.{}.{}'.format(project, dataset, table)
        return self.client.get_table(full_table_name)

    def get_table_column_names(self, project, dataset, table):
        table_info = self.get_table(project, dataset, table)
        return [field.name for field in table_info.schema]

    def download_to_file(self, project, dataset, table, limit=None, offset=None,
                         file_path=None, fail_if_exists=False, progress_bar=True):
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

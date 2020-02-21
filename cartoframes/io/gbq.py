"""Functions to interact with the Google BigQuery platform"""

import os

from google.cloud import bigquery
from google.oauth2.credentials import Credentials

from ..viz.sources import DataFrameSource, BigQuerySource
from ..utils.utils import is_sql_query

PROJECT_KEY = 'GOOGLE_CLOUD_PROJECT'
DATAFRAME_SIZE_LIMIT = 1 * 1024


def prepare_gbq_source(data, project=None, token=None):
    if not isinstance(data, str):
        raise ValueError('Wrong source input. Valid values are str.')

    project = project if project else os.environ[PROJECT_KEY]
    credentials = Credentials(token)

    client = bigquery.Client(project=project, credentials=credentials)
    query = _get_query(data)

    if _estimated_dataframe_size(client, query) < DATAFRAME_SIZE_LIMIT:
        df = _download_dataframe(client, query)
        return DataFrameSource(df, geom_col='geom')
    else:
        data = {
            'project': '',
            'dataset': '',
            'table': '',
            'token': ''
        }
        metadata = {
            'idProperty': 'geoid',
            'properties': {
                'geoid': {'type': 'category'},
                'do_area': {'type': 'number'}
            }
        }
        return BigQuerySource(data, metadata)  # zoom fn


def _download_dataframe(client, query):
    query_job = client.query(query)
    return query_job.to_dataframe()


def _estimated_dataframe_size(client, query):
    # TODO: implement
    return 100


def _get_total_bytes_processed(client, query):
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(query, job_config=job_config)
    return query_job.total_bytes_processed


def _get_query(source):
    return source if is_sql_query(source) else 'SELECT * FROM `{}`'.format(source)

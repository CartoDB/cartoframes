"""Functions to interact with the Google BigQuery platform"""

import os

from google.cloud import bigquery
from google.oauth2.credentials import Credentials

from ..viz.sources import DataFrameSource, BigQuerySource
from ..utils.utils import is_sql_query
from ..utils.logger import log

PROJECT_KEY = 'GOOGLE_CLOUD_PROJECT'
DATA_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB


def prepare_gbq_source(data, project=None, token=None, force_df=False, force_mvt=False):
    if not isinstance(data, str):
        raise ValueError('Wrong source input. Valid values are str.')

    project = project if project else os.environ[PROJECT_KEY]
    credentials = Credentials(token) if token else None

    client = bigquery.Client(project=project, credentials=credentials)
    query = _get_query(data)

    if not force_mvt and (force_df or _estimated_data_size(client, query) < DATA_SIZE_LIMIT):
        log.info('Downloading data. This may take a few seconds')
        df = _download_dataframe(client, query)
        return DataFrameSource(df, geom_col='geom')
    else:
        log.info('Preparing data. This may take a few minutes')
        # TODO: trigger MVT table generation
        # TODO: replace fake data/metadata by real MVT table data
        fake_dataset = 'jarroyo'
        fake_table = 'geography_usa_block_2019_12_mvts'
        data = {
            'projectId': project,
            'datasetId': fake_dataset,
            'tableId': fake_table,
            'token': token
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


def _estimated_data_size(client, query):
    log.info('Estimating size. This may take a few secods')
    estimation_query = '''
        WITH q as ({})
        SELECT SUM(CHAR_LENGTH(ST_ASTEXT(geom))) AS s FROM q
    '''.format(query)
    estimation_query_job = client.query(estimation_query)
    result = estimation_query_job.to_dataframe()
    estimated_size = result.s[0] * 0.425
    if estimated_size < DATA_SIZE_LIMIT:
        log.info('DEBUG: small dataset ({:.2f} KB)'.format(estimated_size / 1024))
    else:
        log.info('DEBUG: big dataset ({:.2f} MB)'.format(estimated_size / 1024 / 1024))
    return estimated_size


def _get_total_bytes_processed(client, query):
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(query, job_config=job_config)
    return query_job.total_bytes_processed


def _get_query(source):
    return source if is_sql_query(source) else 'SELECT * FROM `{}`'.format(source)

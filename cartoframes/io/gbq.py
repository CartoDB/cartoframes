"""Functions to interact with the Google BigQuery platform"""

from .managers.gbq_manager import GBQManager
from ..viz.sources import DataFrameSource, BigQuerySource
from ..utils.utils import is_sql_query
from ..utils.logger import log


def prepare_gbq_source(data, project=None, token=None, force_df=False, force_mvt=False):
    if not isinstance(data, str):
        raise ValueError('Wrong source input. Valid values are str.')

    query = _get_gbq_query(data)
    manager = GBQManager(project, token)

    if not force_mvt and (force_df or manager.estimated_data_size(query) < manager.DATA_SIZE_LIMIT):
        log.info('Downloading data. This may take a few seconds')
        df = manager.download_dataframe(query)
        return DataFrameSource(df, geom_col='geom')
    else:
        log.info('Preparing data. This may take a few minutes')
        data = manager.fetch_mvt_data(query)
        metadata = manager.fetch_mvt_metadata(query)
        manager.trigger_mvt_generation(query)
        return BigQuerySource(data, metadata)  # zoom fn


def _get_gbq_query(source):
    return source if is_sql_query(source) else 'SELECT * FROM `{}`'.format(source)

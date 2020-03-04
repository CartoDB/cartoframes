import time

from . import BaseSource, GBQTilesetSource, GeoDataFrameSource
from ...io.managers.gbq_manager import GBQManager
from ...io.gbq import get_project, get_token
from ...utils.logger import log


class BigQuerySource(BaseSource):
    """BigQuerySource

    """
    def __new__(cls, query=None, table=None, tileset=None,
                project=None, token=None, index_col='geoid', geom_col='geom'):

        query = 'SELECT * FROM `{}`'.format(table) if table else query
        project = project or get_project()
        token = token or get_token()

        if tileset:
            return _gbq_tileset_source(tileset, project, token, index_col)
        elif query:
            return _geo_data_frame_source(query, project, token, geom_col)


def _gbq_tileset_source(tileset, project, token, index_col):
    dataset, table = tileset.split('.')
    data = {
        'projectId': project,
        'datasetId': dataset,
        'tableId': table,
        'token': token
    }
    # TODO: fetch metadata
    metadata = {
        'idProperty': index_col,
        'properties': {'geoid': {'type': 'category'}}
    }
    # TODO: fetch bounds
    bounds = None
    # TODO: fetch zoom mapping
    zoom_fn = '''
        (zoom) => {
            if (zoom > 7) {
                return 7;
            }
            return null;
        }
    '''

    return GBQTilesetSource(data, metadata, bounds, zoom_fn)


def _geo_data_frame_source(query, project, token, geom_col):
    if not isinstance(query, str):
        raise ValueError('Wrong source input. Valid values are str.')

    manager = GBQManager(project, token=token)

    if manager.estimated_data_size(query) < manager.DATA_SIZE_LIMIT:
        log.info('Downloading data. This may take a few seconds')

        begin = time.time()

        df = manager.download_dataframe(query)

        end = time.time()

        print('DEBUG: time elapsed {:.2f}s'.format(end - begin))

        return GeoDataFrameSource(df, geom_col=geom_col)
    else:
        raise Exception('''
        To visualize this dataset you need to create a tileset:

        >>> from cartoframes.io.gbq import create_tileset
        >>> create_tileset(query, 'tileset_table')
        >>> source = BigQuerySource(tileset='tileset_table')
        ''')

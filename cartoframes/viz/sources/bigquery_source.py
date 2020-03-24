import time

from . import BaseSource, GBQTilesetSource, GeoDataFrameSource
from ...io.managers.gbq_manager import GBQManager
from ...utils.logger import log


class BigQuerySource(BaseSource):
    """BigQuerySource
    """
    def __new__(cls, query=None, table=None, tileset=None, project=None, credentials=None, token=None,
                index_col='geoid', geom_col='geom'):
        if tileset is not None:
            return _gbq_tileset_source(tileset, project, token, index_col)

        else:
            if table:
                query = 'SELECT * FROM `{}`'.format(table)

            return _geo_data_frame_source(query, project, token, geom_col)


def _gbq_tileset_source(tileset, project, token, index_col):
    _, dataset, table = GBQManager.split_table_name(tileset)

    # TODO: Check somehow the table is a tileset

    # How to get table metadata and an example of its content, remember the `min` & `max` values are optional
    # manager = GBQManager(project, credentials=None, token=None)
    # table_metadata = manager.get_table_metadata(table_id)
    """
    {
        "input_table": "josema_wip.geography_usa_block_2019_ri",
        "output_table": "josema_wip.geography_usa_block_2019_ri_mvt",
        "available_zooms": [
            {"zoom": 5, "extent": 512}, {"zoom": 6, "extent": 512}, {"zoom": 8, "extent": 512},
            {"zoom": 12, "extent": 4096}, {"zoom": 14, "extent": 4096}
        ],
        "geojson_vt_base_zoom": 12,
        "quadkey_zoom": 15,
        "bbox": [-71.892356, 41.146554, -71.120547, 42.018799],
        "properties": {
            "geoid": {"type": "STRING", "mode": "NULLABLE"},
            "do_label": {"type":"STRING","mode":"NULLABLE"},
            "do_area": {"type": "FLOAT", "mode": "NULLABLE", "min": 1.584, "max": 8897010.568},
            "do_perimeter": {"type": "FLOAT", "mode": "NULLABLE", "min": 6.023,"max": 31377.59},
            "do_num_vertices": {"type": "INTEGER", "mode": "NULLABLE", "min": 4,"max": 2879}
        }
    }
    """

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
    bounds = [[-120, -20], [80, 50]]
    # TODO: Create zoom mapping
    zoom_fn = '''
        (zoom) => {
            if (zoom > 7) {
                return 8;
            }
            if (zoom > 3) {
                return 4;
            }
            return 0;
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

        log.debug('Time elapsed {:.2f}s'.format(end - begin))

        return GeoDataFrameSource(df, geom_col=geom_col)

    else:
        raise Exception("""
            To visualize this dataset you need to create a tileset:

            >>> from cartoframes.io.gbq import create_tileset
            >>> from cartoframes.viz import BigQuerySource
            >>>
            >>> create_tileset('input_table', 'tileset_table', project='project', credentials=credentials)
            >>> source = BigQuerySource(tileset='tileset_table', project='project', credentials=credentials)
        """)

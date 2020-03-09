"""Functions to interact with the Google BigQuery platform"""

from .managers.gbq_manager import GBQManager
from ..utils.utils import create_hash, is_sql_query
from ..utils.logger import log


def create_tileset(source_table, name=None, project=None, credentials=None, token=None, index_col='geoid',
                   geom_col='geom', bbox=None, zooms=None, min_max=False, clean=False):
    prepare_table = _get_prepate_table_name(name)
    manager = GBQManager(project=project, credentials=credentials, token=token)

    log.info('Preparing input data into {} table'.format(prepare_table))
    manager.prepare_input_data(source_table, index_col, geom_col, prepare_table)

    log.info('Creating empty tileset')
    bbox_, quadkey_zoom = manager.create_empty_tileset(prepare_table, bbox, name)

    log.info('Inserting data 1/2')
    manager.insert_geojson_vt_data(prepare_table, bbox_, quadkey_zoom, zooms, name)

    log.info('Inserting data 2/2')
    manager.insert_wasm_data(prepare_table, bbox_, quadkey_zoom, zooms, name)

    if clean:
        log.info('Cleaning temporal data from the {} table'.format(prepare_table))
        manager.clean_prepare_input_data(prepare_table)

    log.info('Generating metadata')
    available_zooms = manager.get_available_zooms(name)
    input_schema = manager.get_input_schema(source_table, index_col, geom_col, min_max)
    manager.update_tileset_metadata(source_table, available_zooms, quadkey_zoom, bbox_, input_schema, name)

    log.info('Tileset {} created'.format(name))


def _get_gbq_query(source):
    return source if is_sql_query(source) else 'SELECT * FROM `{}`'.format(source)


def _get_prepate_table_name(tileset_name):
    project, dataset, table = GBQManager.split_table_name(tileset_name)
    tileset_prefix = '{}.{}'.format(project, dataset) if project else dataset
    return '{}.mvt_prepare_{}'.format(tileset_prefix, create_hash(table))

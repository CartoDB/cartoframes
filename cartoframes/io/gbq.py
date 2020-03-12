"""Functions to interact with the Google BigQuery platform"""

from .managers.gbq_manager import GBQManager
from ..utils.utils import create_hash, get_query_from_table
from ..utils.logger import log


def create_tileset(source, name=None, project=None, credentials=None, token=None, index_col='geoid',
                   geom_col='geom', bbox=None, zooms=None, compression=True, min_max=False, clean=False):
    source_query = get_query_from_table(source)
    prepare_table = _get_prepate_table_name(name)
    manager = GBQManager(project=project, credentials=credentials, token=token)

    log.info('Preparing input data into {} table'.format(prepare_table))
    manager.prepare_input_data(source_query, index_col, geom_col, prepare_table)

    log.info('Creating empty tileset{}'.format(' calculating bounding box' if not bbox else ''))
    bbox_, quadkey_zoom = manager.create_empty_tileset(prepare_table, bbox, name)

    options = {
        'compression': 1
    }
    if not compression:
        options['compression'] = 0

    log.info('Inserting{} MVTs 1/2'.format(' compressed' if compression else ''))
    # manager.insert_geojson_vt_data(prepare_table, bbox_, quadkey_zoom, zooms, options, name)

    log.info('Inserting{} MVTs 2/2'.format(' compressed' if compression else ''))
    manager.insert_wasm_data(prepare_table, bbox_, quadkey_zoom, zooms, options, name)

    if clean:
        log.info('Cleaning temporal data from the {} table'.format(prepare_table))
        manager.clean_prepare_input_data(prepare_table)

    log.info('Generating metadata{}'.format(' with min and max values' if min_max else ''))
    available_zooms = manager.get_available_zooms_oom(name)
    input_schema = manager.get_input_schema(source, index_col, geom_col, min_max)
    manager.update_tileset_metadata(source, available_zooms, quadkey_zoom, compression, bbox_, input_schema, name)

    log.info('Tileset {} created'.format(name))


def _get_prepate_table_name(tileset_name):
    project, dataset, table = GBQManager.split_table_name(tileset_name)
    tileset_prefix = '{}.{}'.format(project, dataset) if project else dataset
    return '{}.mvt_prepare_{}'.format(tileset_prefix, create_hash(table))

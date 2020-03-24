import json
import math
import os

from pathlib import Path

import mercantile

from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from pyproj import Proj, transform

from ...utils.logger import log
from ...utils.utils import get_query_from_table, read_file

PROJECT_KEY = 'GOOGLE_CLOUD_PROJECT'

MAX_LENGTH_TABLE_NAME = 1024

PREPARE_PARTITIONS = 100
MAX_PARTITIONS = 10000
MAX_QUADKEY_ZOOM = 20

WASM_BREAK_ZOOM = 8
GEOJSON_VT_BASE_ZOOM = 12
DEFAULT_ZOOMS = [0, 4, 8, 12, 14]

COMPRESSION_FORMAT = 'pako'

TILE_EXTENT = 4096
TILE_BUFFER = 256

OOM_BASE64 = 'T09N'

# https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#TableFieldSchema.FIELDS.type
BIG_QUERY_NUMBER_TYPES = ['INTEGER', 'INT64', 'FLOAT', 'FLOAT64']

# https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#TableFieldSchema.FIELDS.mode
BIG_QUERY_REPEATED_MODE = 'REPEATED'

TILESET_SQL_DIR = 'gbq_queries'
TILESET_SQL_FILEPATHS = {
    'prepare': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'prepare.sql'),
    'bounding_box': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'bounding_box.sql'),
    'create_table': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'create_table.sql'),
    'insert_geojson_vt': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'insert_geojson_vt.sql'),
    'insert_wasm': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'insert_wasm.sql'),
    'clean': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'clean.sql'),
    'available_zooms_oom': Path(__file__).parent.parent.joinpath(TILESET_SQL_DIR, 'available_zooms_oom.sql')
}


class GBQManager:

    DATA_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    def __init__(self, project=None, credentials=None, token=None):
        self.credentials = Credentials(token) if token else credentials

        self.token = token
        self.project = project if project else os.environ[PROJECT_KEY]
        self.client = bigquery.Client(project=project, credentials=self.credentials)

    def execute_query(self, query):
        query_job = self.client.query(query)
        return query_job.result()

    @classmethod
    def split_table_name(cls, table_name):
        table_name_split = table_name.split('.')

        project = table_name_split[0] if len(table_name_split) == 3 else None
        dataset = table_name_split[-2]
        table = table_name_split[-1]

        return project, dataset, table

    def download_dataframe(self, query):
        query_job = self.client.query(query)
        return query_job.to_dataframe()

    def estimated_data_size(self, query):
        log.info('Estimating size. This may take a few seconds')
        estimation_query = '''
            WITH q as ({})
            SELECT SUM(CHAR_LENGTH(ST_ASTEXT(geom))) AS s FROM q
        '''.format(query)
        estimation_query_job = self.client.query(estimation_query)
        result = estimation_query_job.to_dataframe()
        estimated_size = result.s[0] * 0.425
        if estimated_size < self.DATA_SIZE_LIMIT:
            log.info('DEBUG: small dataset ({:.2f} KB)'.format(estimated_size / 1024))
        else:
            log.info('DEBUG: big dataset ({:.2f} MB)'.format(estimated_size / 1024 / 1024))
        return estimated_size

    def get_table_metadata(self, table_id):
        table_object = self.client.get_table(table_id)
        metadata_string = table_object.description
        return json.loads(metadata_string)

    def get_big_query_table_schema(self, table_id):
        table_object = self.client.get_table(table_id)
        return table_object.schema

    def get_big_query_query_schema(self, query):
        result = self.execute_query('{} LIMIT 1;'.format(query))
        return result.schema

    def prepare_input_data(self, source_query, index_col, geom_col, prepare_table):
        prepare_query = read_file(TILESET_SQL_FILEPATHS['prepare'])
        prepare_query = prepare_query.format(
            source_query=source_query, index_col=index_col, geom_col=geom_col, prepare_partitions=PREPARE_PARTITIONS,
            prepare_table=prepare_table)

        self.execute_query(prepare_query)

    def create_empty_tileset(self, prepare_table, bbox, output_table):
        # Get bounding box if not specified
        if not bbox:
            bbox_query = read_file(TILESET_SQL_FILEPATHS['bounding_box'])
            bbox_query = bbox_query.format(prepare_table=prepare_table)

            bbox_result = self.execute_query(bbox_query)

            for row in bbox_result:
                bbox_3857 = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]

            proj_3857 = Proj('epsg:3857')
            proj_4326 = Proj('epsg:4326')

            xmin, ymin = transform(proj_3857, proj_4326, bbox_3857[0], bbox_3857[1], always_xy=True)
            xmax, ymax = transform(proj_3857, proj_4326, bbox_3857[2], bbox_3857[3], always_xy=True)

            bbox = [xmin, ymin, xmax, ymax]

        # Guess best quadkey
        quadkey_zoom = 1
        while True:
            min_tile = mercantile.tile(bbox[0], bbox[3], quadkey_zoom)  # min_tile in quadkey is upper left
            max_tile = mercantile.tile(bbox[2], bbox[1], quadkey_zoom)  # max_tile in quadkey is bottom right

            min_quadkey = mercantile.quadkey(min_tile)
            max_quadkey = mercantile.quadkey(max_tile)

            min_integer_quadkey = int(min_quadkey, 4)
            max_integer_quadkey = int(max_quadkey, 4)

            if (max_integer_quadkey - min_integer_quadkey) >= MAX_PARTITIONS or quadkey_zoom == MAX_QUADKEY_ZOOM:
                break

            else:
                quadkey_zoom += 1

        step_integer_queadkey = math.ceil((max_integer_quadkey - min_integer_quadkey) / MAX_PARTITIONS)

        create_table_query = read_file(TILESET_SQL_FILEPATHS['create_table'])
        create_table_query = create_table_query.format(
            min_integer_quadkey=min_integer_quadkey, max_integer_quadkey=max_integer_quadkey,
            step_integer_queadkey=step_integer_queadkey, output_table=output_table)

        self.execute_query(create_table_query)

        return bbox, quadkey_zoom

    def insert_geojson_vt_data(self, prepare_table, bbox, quadkey_zoom, zooms, options, output_table):
        zooms_ = zooms if zooms else DEFAULT_ZOOMS
        options_ = json.dumps(options)

        geojson_vt_base_zooms = [GEOJSON_VT_BASE_ZOOM]
        geojson_vt_zooms = [zoom - GEOJSON_VT_BASE_ZOOM for zoom in zooms_ if zoom >= GEOJSON_VT_BASE_ZOOM]

        if not geojson_vt_zooms:
            return

        insert_geojson_vt_query = read_file(TILESET_SQL_FILEPATHS['insert_geojson_vt'])
        insert_geojson_vt_query = insert_geojson_vt_query.format(
            prepare_table=prepare_table, xmin=bbox[0], ymin=bbox[1], xmax=bbox[2], ymax=bbox[3],
            geojson_vt_base_zooms=geojson_vt_base_zooms, geojson_vt_zooms=geojson_vt_zooms, quadkey_zoom=quadkey_zoom,
            tile_extent=TILE_EXTENT, tile_buffer=TILE_BUFFER, options=options_, output_table=output_table)

        self.execute_query(insert_geojson_vt_query)

    def insert_wasm_data(self, prepare_table, bbox, quadkey_zoom, zooms, options, output_table):
        zooms_ = zooms if zooms else DEFAULT_ZOOMS
        options_ = json.dumps(options)

        wasm_zooms = [zoom for zoom in zooms_ if zoom < GEOJSON_VT_BASE_ZOOM]

        wasm_little_zooms = [wasm_zoom for wasm_zoom in wasm_zooms if wasm_zoom <= WASM_BREAK_ZOOM]
        wasm_big_zooms = [wasm_zoom for wasm_zoom in wasm_zooms if wasm_zoom > WASM_BREAK_ZOOM]

        self._insert_wasm_data(prepare_table, bbox, quadkey_zoom, wasm_little_zooms, options_, output_table)
        for wasm_big_zoom in wasm_big_zooms:
            self._insert_wasm_data(prepare_table, bbox, quadkey_zoom, [wasm_big_zoom], options_, output_table)

    def _insert_wasm_data(self, prepare_table, bbox, quadkey_zoom, wasm_zooms, options_, output_table):
        if not wasm_zooms:
            return

        insert_wasm_query = read_file(TILESET_SQL_FILEPATHS['insert_wasm'])
        insert_wasm_query = insert_wasm_query.format(
            prepare_table=prepare_table, xmin=bbox[0], ymin=bbox[1], xmax=bbox[2], ymax=bbox[3], wasm_zooms=wasm_zooms,
            quadkey_zoom=quadkey_zoom, tile_extent=TILE_EXTENT, tile_buffer=TILE_BUFFER, options=options_,
            output_table=output_table)

        self.execute_query(insert_wasm_query)

    def clean_prepare_input_data(self, prepare_table):
        clean_query = read_file(TILESET_SQL_FILEPATHS['clean'])
        clean_query = clean_query.format(prepare_table=prepare_table)

        self.execute_query(clean_query)

    def get_available_zooms_oom(self, output_table):
        available_zooms_oom_query = read_file(TILESET_SQL_FILEPATHS['available_zooms_oom'])
        available_zooms_oom_query = available_zooms_oom_query.format(oom_base64=OOM_BASE64, output_table=output_table)

        available_zooms = []
        available_zooms_oom_result = self.execute_query(available_zooms_oom_query)
        for row in available_zooms_oom_result:
            available_zooms.append({
                'zoom': row['zoom'],
                'oom_ratio': row['oom_ratio']
            })

        return available_zooms

    def get_input_schema(self, source, index_col, geom_col, min_max):
        source_query = get_query_from_table(source)

        if source_query in (source, source[:-1]):  # `source` is a SQL query
            fields = self.get_big_query_query_schema(source_query)

        else:  # `source` is a table
            fields = self.get_big_query_table_schema(source)

        min_max_names = []
        min_max_select = []
        schema = {}

        # Getting and formatting schema, and the query for min and max values
        for field in fields:
            if field.name == geom_col:
                continue

            name = index_col if field.name == index_col else field.name

            if field.field_type in BIG_QUERY_NUMBER_TYPES and field.mode != BIG_QUERY_REPEATED_MODE:
                min_max_names.append(name)
                min_max_select.extend(['MIN({}) AS {}_min'.format(field.name, name),
                                       'MAX({}) AS {}_max'.format(field.name, name)])

            schema[name] = {
                'type': field.field_type,
                'mode': field.mode
            }

        # Obtaining min and max values for integers and floats
        if min_max:
            min_max_query = 'SELECT {} FROM ({}) q;'.format(', '.join(min_max_select), source_query)
            min_max_result = self.execute_query(min_max_query)
            for row in min_max_result:
                for name in min_max_names:
                    schema[name]['min'] = row['{}_min'.format(name)]
                    schema[name]['max'] = row['{}_max'.format(name)]

        return schema

    def update_tileset_metadata(self, source, available_zooms, quadkey_zoom, compression, bbox, input_schema,
                                output_table):
        metadata_dict = {
            'source': source,
            'available_zooms': available_zooms,
            'tile_extent': TILE_EXTENT,
            'geojson_vt_base_zoom': GEOJSON_VT_BASE_ZOOM,
            'quadkey_zoom': quadkey_zoom,
            'compression': COMPRESSION_FORMAT if compression else None,
            'bbox': bbox,
            'properties': input_schema
        }

        table_object = self.client.get_table(output_table)
        table_object.description = json.dumps(metadata_dict)
        self.client.update_table(table_object, ['description'])

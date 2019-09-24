import uuid

from ..clients import bigquery_client
from ...auth import get_default_credentials
from .enrichment_utils import copy_data_and_generate_enrichment_id, process_filters, get_tables_and_variables

_ENRICHMENT_ID = 'enrichment_id'
_WORKING_PROJECT = 'carto-do-customers'

# TODO: process column name in metadata, remove spaces and points


def enrich_points(data, variables, data_geom_column='geometry', filters=dict(), credentials=None):

    credentials = credentials or get_default_credentials()
    bq_client = bigquery_client.BigQueryClient(credentials)

    user_dataset = credentials.username.replace('-', '_')

    data_copy = copy_data_and_generate_enrichment_id(data, _ENRICHMENT_ID, data_geom_column)

    data_geometry_id_copy = data_copy[[data_geom_column, _ENRICHMENT_ID]]
    schema = {data_geom_column: 'GEOGRAPHY', _ENRICHMENT_ID: 'INTEGER'}

    id_tablename = uuid.uuid4().hex
    data_tablename = 'temp_{id}'.format(id=id_tablename)

    bq_client.upload_dataframe(data_geometry_id_copy, schema, data_tablename,
                               project=_WORKING_PROJECT, dataset=user_dataset, ttl_days=1)

    table_data_enrichment, table_geo_enrichment, variables_list = get_tables_and_variables(variables)

    filters_str = process_filters(filters)

    sql = __prepare_sql(_ENRICHMENT_ID, variables_list, table_data_enrichment, table_geo_enrichment,
                        user_dataset, _WORKING_PROJECT, user_dataset,
                        data_tablename, data_geom_column, filters_str)

    data_geometry_id_enriched = bq_client.query(sql).to_dataframe()

    data_copy = data_copy.merge(data_geometry_id_enriched, on=_ENRICHMENT_ID, how='left')\
        .drop(_ENRICHMENT_ID, axis=1)

    return data_copy


def __prepare_sql(enrichment_id, variables, enrichment_table, enrichment_geo_table, user_dataset,
                  working_project, working_dataset, data_table, data_geom_column, filters):

    sql = '''
        SELECT data_table.{enrichment_id},
              {variables},
              ST_Area(enrichment_geo_table.geom) AS area,
              NULL AS population
        FROM `carto-do-customers.{user_dataset}.{enrichment_table}` enrichment_table
        JOIN `carto-do-customers.{user_dataset}.{enrichment_geo_table}` enrichment_geo_table
          ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{working_project}.{working_dataset}.{data_table}` data_table
          ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {filters};
    '''.format(enrichment_id=enrichment_id, variables=', '.join(variables),
               enrichment_table=enrichment_table, enrichment_geo_table=enrichment_geo_table,
               user_dataset=user_dataset, working_project=working_project,
               working_dataset=working_dataset, data_table=data_table,
               data_geom_column=data_geom_column, filters=filters)

    return sql

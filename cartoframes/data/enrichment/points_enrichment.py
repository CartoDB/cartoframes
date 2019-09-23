import uuid

from ..clients import bigquery_client
from ...auth import get_default_credentials
from collections import defaultdict


_ENRICHMENT_ID = 'enrichment_id'
_WORKING_PROJECT = 'carto-do-customers'

# TODO: process column name in metadata, remove spaces and points


def enrich_points(data, variables, data_geom_column='geometry', filters=dict(), credentials=None):

    credentials = credentials or get_default_credentials()
    bq_client = bigquery_client.BigQueryClient(credentials)

    user_workspace = credentials.username.replace('-', '_')

    data_copy = __copy_data_and_generate_enrichment_id(data, _ENRICHMENT_ID)

    data_geometry_id_copy = data_copy[[data_geom_column, _ENRICHMENT_ID]]
    schema = {data_geom_column: 'GEOGRAPHY', _ENRICHMENT_ID: 'INTEGER'}

    id_tablename = uuid.uuid4().hex
    data_tablename = 'temp_{id}'.format(id=id_tablename)

    bq_client.upload_dataframe(data_geometry_id_copy, schema, data_tablename,
                               project=_WORKING_PROJECT, dataset=user_workspace)

    table_data_enrichment, table_geo_enrichment, variables_list = __get_tables_and_variables(variables)

    filters_str = __process_filters(filters)

    sql = __prepare_sql(_ENRICHMENT_ID, variables_list, table_data_enrichment, table_geo_enrichment,
                        credentials.username, _WORKING_PROJECT, user_workspace,
                        data_tablename, data_geom_column, filters_str)

    data_geometry_id_enriched = bq_client.query(sql).to_dataframe()

    data_copy = data_copy.merge(data_geometry_id_enriched, on=_ENRICHMENT_ID, how='left')\
        .drop(_ENRICHMENT_ID, axis=1)

    bq_client.delete_table(data_tablename, project=_WORKING_PROJECT, dataset=user_workspace)

    return data_copy


def __prepare_sql(enrichment_id, variables, enrichment_table, enrichment_geo_table, user_workspace,
                  working_project, working_dataset, data_table, data_geom_column, filters):

    sql = '''
        SELECT data_table.{enrichment_id},
              {variables},
              ST_Area(enrichment_geo_table.geom) AS area,
              NULL AS population
        FROM `carto-do-customers.{user_workspace}.{enrichment_table}` enrichment_table
        JOIN `carto-do-customers.{user_workspace}.{enrichment_geo_table}` enrichment_geo_table
          ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{working_project}.{working_dataset}.{data_table}` data_table
          ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {filters};
    '''.format(enrichment_id=enrichment_id, variables=', '.join(variables),
               enrichment_table=enrichment_table, enrichment_geo_table=enrichment_geo_table,
               user_workspace=user_workspace.replace('-', '_'), working_project=working_project,
               working_dataset=working_dataset, data_table=data_table,
               data_geom_column=data_geom_column, filters=filters)

    return sql


def __copy_data_and_generate_enrichment_id(data, enrichment_id_column):
    data_copy = data.copy()
    data_copy[_ENRICHMENT_ID] = range(data_copy.shape[0])

    return data_copy


def __get_tables_and_variables(variables):
    variables_id = variables['id'].tolist()
    table_to_variables = __process_enrichment_variables(variables_id)
    table_data_enrichment = list(table_to_variables.keys()).pop()
    table_geo_enrichment = __get_name_geotable_from_datatable(table_data_enrichment)
    variables_list = list(table_to_variables.values()).pop()

    return table_data_enrichment, table_geo_enrichment, variables_list


def __process_enrichment_variables(variables):
    table_to_variables = defaultdict(list)

    for variable in variables:
        variable_split = variable.split('.')
        table, variable = variable_split[-2], variable_split[-1]

        table_to_variables[table].append(variable)

    return table_to_variables


def __get_name_geotable_from_datatable(datatable):
    datatable_split = datatable.split('_')
    geo_information = datatable_split[2:5]
    geotable = 'geography_{geo_information_joined}'.format(geo_information_joined='_'.join(geo_information))

    return geotable


def __process_filters(filters_dict):
    filters = ''
    # TODO: Add data table ref in fields of filters
    if filters_dict:
        filters_list = list()

        for key, value in filters_dict.items():
            filters_list.append('='.join(["{}".format(key), "'{}'".format(value)]))

        filters = ' AND '.join(filters_list)
        filters = 'WHERE {filters}'.format(filters=filters)

    return filters

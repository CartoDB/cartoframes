import uuid

from . import bigquery_client
from ...auth import get_default_credentials
from collections import defaultdict


_ENRICHMENT_ID = 'enrichment_id'

# TODO: process column name in metadata, remove spaces and points 


def enrich_points(data, variables, data_geom_column='geometry', filters=dict()):

    credentials = get_default_credentials()

    bq_client = bigquery_client.BigQueryClient(credentials)

    # Copy dataframe and generate id to join to original data later
    data_copy = data.copy()
    data_copy[_ENRICHMENT_ID] = range(data_copy.shape[0])
    data_geometry_id_copy = data_copy[[_ENRICHMENT_ID, data_geom_column]]

    data_tablename = uuid.uuid4().hex

    bq_client.upload_dataframe(data_geometry_id_copy, _ENRICHMENT_ID, data_geom_column, data_tablename)

    variables_id = variables['id'].tolist()
    table_to_variables = __process_enrichment_variables(variables_id)
    table_data_enrichment = list(table_to_variables.keys()).pop()
    table_geo_enrichment = __get_name_geotable_from_datatable(table_data_enrichment)
    variables_list = list(table_to_variables.values()).pop()

    filters_str = __process_filters(filters)

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
    '''.format(enrichment_id=_ENRICHMENT_ID, variables=', '.join(variables_list),
               enrichment_table=table_data_enrichment, enrichment_geo_table=table_geo_enrichment,
               user_workspace=credentials.username.replace('-', '_'), working_project=bigquery_client._WORKING_PROJECT,
               working_dataset=bigquery_client._TEMP_DATASET_ENRICHMENT, data_table=data_tablename,
               data_geom_column=data_geom_column, filters=filters_str)

    data_geometry_id_augmentated = bq_client.query(sql).to_dataframe()

    data_augmentated = data_copy.merge(data_geometry_id_augmentated, on=_ENRICHMENT_ID, how='left')\
        .drop(_ENRICHMENT_ID, axis=1)

    bq_client.delete_table(data_tablename)

    return data_augmentated


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

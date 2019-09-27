import pandas as pd
import geopandas as gpd
import geojson
import uuid

from shapely.geometry import shape
from shapely.wkt import loads
from ..dataset.dataset import Dataset
from collections import defaultdict
from ...exceptions import EnrichmentException
from ...auth import get_default_credentials
from ..clients import bigquery_client

_ENRICHMENT_ID = 'enrichment_id'
_WORKING_PROJECT = 'carto-do-customers'


def enrich(preparation_sql_function, **kwargs):

    credentials = kwargs['credentials'] or get_default_credentials()
    bq_client = bigquery_client.BigQueryClient(credentials)

    user_dataset = credentials.username.replace('-', '_')

    data_copy = copy_data_and_generate_enrichment_id(kwargs['data'], _ENRICHMENT_ID, kwargs['data_geom_column'])

    data_copy[kwargs['data_geom_column']] = data_copy[kwargs['data_geom_column']].apply(wkt_to_geojson)

    data_geometry_id_copy = data_copy[[kwargs['data_geom_column'], _ENRICHMENT_ID]]
    schema = {kwargs['data_geom_column']: 'GEOGRAPHY', _ENRICHMENT_ID: 'INTEGER'}

    id_tablename = uuid.uuid4().hex
    data_tablename = 'temp_{id}'.format(id=id_tablename)

    bq_client.upload_dataframe(data_geometry_id_copy, schema, data_tablename,
                               project=_WORKING_PROJECT, dataset=user_dataset, ttl_days=1)

    table_data_enrichment, table_geo_enrichment, variables_list = get_tables_and_variables(kwargs['variables'])

    filters_str = process_filters(kwargs['filters'])

    sql = preparation_sql_function(_ENRICHMENT_ID, filters_str, variables_list, table_data_enrichment,
                                   table_geo_enrichment, user_dataset, _WORKING_PROJECT, data_tablename,
                                   **kwargs)

    data_geometry_id_enriched = bq_client.query(sql).to_dataframe()

    data_copy = data_copy.merge(data_geometry_id_enriched, on=_ENRICHMENT_ID, how='left')\
        .drop(_ENRICHMENT_ID, axis=1)

    data_copy[kwargs['data_geom_column']] = data_copy[kwargs['data_geom_column']].apply(geojson_to_wkt)

    return data_copy


def copy_data_and_generate_enrichment_id(data, enrichment_id_column, geometry_column):

    if isinstance(data, Dataset):
        data = data.dataframe

    data_copy = data.copy()
    data_copy[enrichment_id_column] = range(data_copy.shape[0])

    if isinstance(data_copy, gpd.GeoDataFrame):
        data_copy[geometry_column] = data_copy[geometry_column].apply(lambda geometry: geometry.wkt)

    return data_copy


def wkt_to_geojson(wkt):
    shapely_geom = loads(wkt)
    geojson_geometry = geojson.Feature(geometry=shapely_geom, properties={})

    return str(geojson_geometry.geometry)


def geojson_to_wkt(geojson_str):
    geojson_geom = geojson.loads(geojson_str)
    wkt_geometry = shape(geojson_geom)

    shapely_geom = loads(wkt_geometry.wkt)

    return shapely_geom


def process_filters(filters_dict):
    filters = ''
    # TODO: Add data table ref in fields of filters
    if filters_dict:
        filters_list = list()

        for key, value in filters_dict.items():
            filters_list.append('='.join(["{}".format(key), "'{}'".format(value)]))

        filters = ' AND '.join(filters_list)
        filters = 'WHERE {filters}'.format(filters=filters)

    return filters


def get_tables_and_variables(variables):

    if isinstance(variables, pd.Series):
        variables_id = [variables['id']]
    elif isinstance(variables, pd.DataFrame):
        variables_id = variables['id'].tolist()
    else:
        raise EnrichmentException('Variable(s) to enrich should be an instance of Series or DataFrame')

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

import uuid
import geopandas as gpd

from collections import defaultdict

from ..catalog.variable import Variable
from ..catalog.dataset import CatalogDataset
from ...dataset.dataset import Dataset
from ...clients import bigquery_client
from ....auth import get_default_credentials
from ....exceptions import EnrichmentException
from ....utils.geom_utils import _compute_geometry_from_geom, geojson_to_wkt, wkt_to_geojson


_ENRICHMENT_ID = 'enrichment_id'
_WORKING_PROJECT = 'carto-do-customers'
_PUBLIC_PROJECT = 'carto-do-public-data'
_PUBLIC_DATASET = 'open_data'


def enrich(query_function, **kwargs):
    credentials = _get_credentials(kwargs['credentials'])
    user_dataset = credentials.get_do_dataset()
    bq_client = _get_bigquery_client(_WORKING_PROJECT, credentials)

    data_copy = _prepare_data(kwargs['data'], kwargs['data_geom_column'])
    tablename = _upload_dataframe(bq_client, user_dataset, data_copy, kwargs['data_geom_column'])

    queries = _enrichment_queries(user_dataset, tablename, query_function, **kwargs)

    data_enriched = _execute_enrichment(bq_client, queries, data_copy, kwargs['data_geom_column'])

    data_enriched[kwargs['data_geom_column']] = _compute_geometry_from_geom(data_enriched[kwargs['data_geom_column']])

    return data_enriched


def _get_credentials(credentials=None):
    return credentials or get_default_credentials()


def _get_bigquery_client(project, credentials):
    return bigquery_client.BigQueryClient(project, credentials)


def _prepare_data(data, data_geom_column):
    data_copy = __copy_data_and_generate_enrichment_id(data, _ENRICHMENT_ID, data_geom_column)
    data_copy[data_geom_column] = data_copy[data_geom_column].apply(wkt_to_geojson)
    return data_copy


def _upload_dataframe(bq_client, user_dataset, data_copy, data_geom_column):
    data_geometry_id_copy = data_copy[[data_geom_column, _ENRICHMENT_ID]]
    schema = {data_geom_column: 'GEOGRAPHY', _ENRICHMENT_ID: 'INTEGER'}

    id_tablename = uuid.uuid4().hex
    data_tablename = 'temp_{id}'.format(id=id_tablename)

    bq_client.upload_dataframe(data_geometry_id_copy, schema, data_tablename,
                               project=_WORKING_PROJECT, dataset=user_dataset)

    return data_tablename


def _enrichment_queries(user_dataset, tablename, query_function, **kwargs):
    is_polygon_enrichment = 'agg_operators' in kwargs
    variables = __process_variables(kwargs['variables'], is_polygon_enrichment)

    table_to_geotable, table_to_variables,\
        table_to_project, table_to_dataset = __process_enrichment_variables(variables, user_dataset)

    filters_str = __process_filters(kwargs['filters'])

    if kwargs.get('agg_operators') is not None:
        kwargs['agg_operators'] = __process_agg_operators(kwargs['agg_operators'], variables)

    return query_function(_ENRICHMENT_ID, filters_str, table_to_geotable, table_to_variables, table_to_project,
                          table_to_dataset, user_dataset, _WORKING_PROJECT, tablename, **kwargs)


def _execute_enrichment(bq_client, queries, data_copy, data_geom_column):

    dfs_enriched = list()

    for query in queries:

        df_enriched = bq_client.query(query).to_dataframe()

        dfs_enriched.append(df_enriched)

    for df in dfs_enriched:
        data_copy = data_copy.merge(df, on=_ENRICHMENT_ID, how='left')

    data_copy.drop(_ENRICHMENT_ID, axis=1, inplace=True)
    data_copy[data_geom_column] = data_copy[data_geom_column].apply(geojson_to_wkt)

    return data_copy


def __copy_data_and_generate_enrichment_id(data, enrichment_id_column, geometry_column):

    has_to_decode_geom = True

    if isinstance(data, Dataset):
        if data.dataframe is None:
            has_to_decode_geom = False
            geometry_column = 'the_geom'
            data.download(decode_geom=True)

        data = data.dataframe
    elif isinstance(data, gpd.GeoDataFrame):
        has_to_decode_geom = False

    data_copy = data.copy()
    data_copy[enrichment_id_column] = range(data_copy.shape[0])

    if has_to_decode_geom:
        data_copy[geometry_column] = _compute_geometry_from_geom(data_copy[geometry_column])

    data_copy[geometry_column] = data_copy[geometry_column].apply(lambda geometry: geometry.wkt)

    return data_copy


def __process_variables(variables, is_polygon_enrichment):
    variables_result = list()
    if isinstance(variables, Variable):
        variables_result = [variables]
    elif isinstance(variables, str):
        variables_result = [Variable.get(variables)]
    elif isinstance(variables, list):
        first_element = variables[0]

        if isinstance(first_element, str):
            variables_result = Variable.get_list(variables)
        else:
            variables_result = variables
    else:
        raise EnrichmentException('Variable(s) to enrich should be an instance of Variable / CatalogList / str / list')

    if is_polygon_enrichment:
        variables_result = [variable for variable in variables_result if variable.agg_method is not None]

    return variables_result


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


def __process_agg_operators(agg_operators, variables):
    if isinstance(agg_operators, str):
        agg_operators_result = dict()

        for variable in variables:
            agg_operators_result[variable.column_name] = agg_operators

    elif isinstance(agg_operators, dict):
        agg_operators_result = agg_operators.copy()

        for variable in variables:
            if variable.column_name not in agg_operators_result:
                agg_operators_result[variable.column_name] = variable.agg_method
    else:
        raise EnrichmentException('agg_operators param must be a string or a dict')

    return agg_operators_result


def __process_enrichment_variables(variables, user_dataset):
    table_to_geotable = dict()
    table_to_variables = defaultdict(list)
    table_to_project = dict()
    table_to_dataset = dict()

    for variable in variables:
        project_name = variable.project_name
        dataset_name = variable.schema_name
        table_name = variable.dataset_name
        variable_name = variable.column_name
        dataset_geotable, geotable = __get_properties_geotable(variable)

        if project_name != _PUBLIC_PROJECT:
            table_name = 'view_{dataset}_{table}'.format(dataset=dataset_name,
                                                         table=table_name,
                                                         user_dataset=user_dataset)

        if table_name not in table_to_dataset:
            if project_name != _PUBLIC_PROJECT:
                table_to_dataset[table_name] = user_dataset
            else:
                table_to_dataset[table_name] = _PUBLIC_DATASET

        if table_name not in table_to_geotable:
            if project_name != _PUBLIC_PROJECT:
                geotable = 'view_{dataset}_{geotable}'.format(dataset=dataset_geotable,
                                                              geotable=geotable)
            table_to_geotable[table_name] = geotable

        if table_name not in table_to_project:
            if project_name == _PUBLIC_PROJECT:
                table_to_project[table_name] = _PUBLIC_PROJECT
            else:
                table_to_project[table_name] = _WORKING_PROJECT

        table_to_variables[table_name].append(variable_name)

    return table_to_geotable, table_to_variables, table_to_project, table_to_dataset


def __get_properties_geotable(variable):

    geography_id = CatalogDataset.get(variable.dataset).geography

    _, geo_dataset, geo_table = geography_id.split('.')

    return geo_dataset, geo_table

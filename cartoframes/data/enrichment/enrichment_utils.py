import pandas as pd
import geopandas as gpd

from ..dataset.dataset import Dataset
from collections import defaultdict
from ...exceptions import EnrichmentException


def copy_data_and_generate_enrichment_id(data, enrichment_id_column, geometry_column):

    if isinstance(data, Dataset):
        data = data.dataframe

    data_copy = data.copy()
    data_copy[enrichment_id_column] = range(data_copy.shape[0])

    if isinstance(data_copy, gpd.GeoDataFrame):
        data_copy[geometry_column] = data_copy[geometry_column].apply(lambda geometry: geometry.wkt)

    return data_copy


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

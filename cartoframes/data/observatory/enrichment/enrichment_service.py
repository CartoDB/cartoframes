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
_DEFAULT_PROJECT = 'carto-do'
_WORKING_PROJECT = 'carto-do-customers'
_PUBLIC_PROJECT = 'carto-do-public-data'

AGGREGATION_DEFAULT = 'default'
AGGREGATION_NONE = 'none'


class VariableAggregation(object):
    """Class to overwrite a `<cartoframes.data.observatory> Variable` default aggregation method in
        enrichment funcitons

        Example:
            VariableAggregation(variable, 'SUM')
    """
    def __init__(self, variable, aggregation=None):
        self.variable = _prepare_variable(variable)
        self.aggregation = aggregation


class VariableFilter(object):
    """Class for filtering in enrichment. It receives 3 parameters: variable: a
        `<cartoframes.data.observatory> Variable` instance,
        operator: the operation to do over the variable column in SQL syntax and
        value: the value to be used in the SQL operation

        Examples:
            Equal to number: VariableFilter(variable, '= 3')
            Equal to string: VariableFilter(variable, "= 'the string'")
            Greater that 3: VariableFilter(variable, '> 3')
    """
    def __init__(self, variable, query):
        self.variable = _prepare_variable(variable)
        self.query = query


class EnrichmentService(object):
    """Base class for the Enrichment utility with commons auxiliary methods"""

    def __init__(self, credentials=None):
        self.credentials = credentials = credentials or get_default_credentials()
        self.user_dataset = self.credentials.get_do_user_dataset()
        self.bq_client = bigquery_client.BigQueryClient(_WORKING_PROJECT, credentials)
        self.working_project = _WORKING_PROJECT
        self.enrichment_id = _ENRICHMENT_ID
        self.public_project = _PUBLIC_PROJECT

    def _execute_enrichment(self, queries, data, data_geom_column):
        dfs_enriched = list()

        for query in queries:
            df_enriched = self.bq_client.query(query).to_dataframe()
            dfs_enriched.append(df_enriched)

        for df in dfs_enriched:
            data = data.merge(df, on=self.enrichment_id, how='left')

        data.drop(self.enrichment_id, axis=1, inplace=True)
        data[data_geom_column] = data[data_geom_column].apply(geojson_to_wkt)

        data[data_geom_column] = _compute_geometry_from_geom(data[data_geom_column])

        return data

    def _prepare_data(self, data, data_geom_column):
        data_copy = self.__copy_data_and_generate_enrichment_id(data, data_geom_column)
        data_copy[data_geom_column] = data_copy[data_geom_column].apply(wkt_to_geojson)
        return data_copy

    def _get_temp_table_name(self):
        id_tablename = uuid.uuid4().hex
        return 'temp_{id}'.format(id=id_tablename)

    def _upload_dataframe(self, tablename, data_copy, data_geom_column):
        data_geometry_id_copy = data_copy[[data_geom_column, self.enrichment_id]]
        schema = {data_geom_column: 'GEOGRAPHY', self.enrichment_id: 'INTEGER'}

        self.bq_client.upload_dataframe(
            dataframe=data_geometry_id_copy,
            schema=schema,
            tablename=tablename,
            project=self.working_project,
            dataset=self.user_dataset
        )

    def _get_tables_metadata(self, variables):
        tables_metadata = defaultdict(lambda: defaultdict(list))

        for variable in variables:
            if isinstance(variable, VariableAggregation):
                variable_aggregation = variable
                table_name = self.__get_enrichment_table(variable_aggregation.variable)
                tables_metadata[table_name]['variables'].append(variable_aggregation)
                variable = variable_aggregation.variable
            else:
                table_name = self.__get_enrichment_table(variable)
                tables_metadata[table_name]['variables'].append(variable)

            if 'dataset' not in tables_metadata[table_name].keys():
                tables_metadata[table_name]['dataset'] = self.__get_dataset(variable, table_name)

            if 'geo_table' not in tables_metadata[table_name].keys():
                tables_metadata[table_name]['geo_table'] = self.__get_geo_table(variable)

            if 'project' not in tables_metadata[table_name].keys():
                tables_metadata[table_name]['project'] = self.__get_project(variable)

        return tables_metadata

    def __get_enrichment_table(self, variable):
        if variable.project_name != self.public_project:
            return 'view_{dataset}_{table}'.format(
                dataset=variable.schema_name,
                table=variable.dataset_name
            )
        else:
            return variable.dataset_name

    def __get_dataset(self, variable, table_name):
        if variable.project_name != self.public_project:
            return '{project}.{dataset}.{table_name}'.format(
                project=self.working_project,
                dataset=self.user_dataset,
                table_name=table_name
            )
        else:
            return variable.dataset

    def __get_geo_table(self, variable):
        geography_id = CatalogDataset.get(variable.dataset).geography
        _, dataset_geo_table, geo_table = geography_id.split('.')

        if variable.project_name != self.public_project:
            return '{project}.{dataset}.view_{dataset_geo_table}_{geo_table}'.format(
                project=self.working_project,
                dataset=self.user_dataset,
                dataset_geo_table=dataset_geo_table,
                geo_table=geo_table
            )
        else:
            return '{project}.{dataset}.{geo_table}'.format(
                project=self.public_project,
                dataset=dataset_geo_table,
                geo_table=geo_table
            )

    def __get_project(self, variable):
        project = self.public_project

        if variable.project_name != self.public_project:
            project = self.working_project

        return project

    def __copy_data_and_generate_enrichment_id(self, data, geometry_column):
        has_to_decode_geom = True
        enrichment_id_column = self.enrichment_id

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


def prepare_variables(variables):
    if isinstance(variables, list):
        return [_prepare_variable(var) for var in variables]
    else:
        return [_prepare_variable(variables)]


def _prepare_variable(variable):
    if isinstance(variable, str):
        variable = Variable.get(variable)

    if not isinstance(variable, Variable):
        raise EnrichmentException("""
            variable should be a `<cartoframes.data.observatory> Variable` instance,
            Variable `id` property or Variable `slug` property
        """)

    return variable


def get_variable_aggregations(variables, aggregation):
    return [VariableAggregation(variable, __get_aggregation(variable, aggregation)) for variable in variables]


def __get_aggregation(variable, aggregation):
    if aggregation == AGGREGATION_NONE:
        return None
    elif aggregation == AGGREGATION_DEFAULT:
        return variable.agg_method or 'array_agg'
    elif isinstance(aggregation, str):
        return aggregation
    elif isinstance(aggregation, list):
        agg = variable.agg_method or 'array_agg'
        for variable_aggregation in aggregation:
            if variable_aggregation.variable == variable:
                agg = variable_aggregation.aggregation
                break

        return agg

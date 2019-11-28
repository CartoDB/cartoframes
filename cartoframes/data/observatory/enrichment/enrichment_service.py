import uuid

from collections import defaultdict
import warnings

from ..catalog.variable import Variable
from ..catalog.dataset import Dataset
from ..catalog.geography import Geography
from ...clients import bigquery_client
from ....auth import get_default_credentials
from ....exceptions import EnrichmentException
from ....core.cartodataframe import CartoDataFrame
from ....utils.geom_utils import to_geojson


_ENRICHMENT_ID = 'enrichment_id'
_GEOJSON_COLUMN = '__geojson_geom'
_DEFAULT_PROJECT = 'carto-do'
_WORKING_PROJECT = 'carto-do-customers'
_PUBLIC_PROJECT = 'carto-do-public-data'

AGGREGATION_DEFAULT = 'default'
AGGREGATION_NONE = 'none'


class VariableAggregation(object):
    """This class overwrites a :py:class:`Variable <cartoframes.data.observatory.Variable>` default aggregation method in
        :py:class:`Enrichment <cartoframes.data.observatory.Enrichment>` functions

        Args:
            variable (str or :obj:`Variable`):
                The variable name or :obj:`Variable` instance

            aggregation (str):
                The aggregation method, it can be one of these values: 'MIN', 'MAX', 'SUM', 'AVG', 'COUNT',
                'ARRAY_AGG', 'ARRAY_CONCAT_AGG', 'STRING_AGG' but check this
                `documentation <https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions>`__
                for a complete list of aggregate functions

        Returns:
            :py:class:`VariableAggregation <cartoframes.data.observatory.entity.VariableAggregation>`

        Example:

            Next example uses a `VariableAggregation` instance to calculate the `SUM` of car-free households
            :obj:`Variable` of the :obj:`Catalog` for each polygon of `my_local_dataframe` pandas `DataFrame`

            .. code::

                from cartoframes.data.observatory import Enrichment, Variable, VariableAggregation

                variable = Variable.get('no_cars_d19dfd10')
                enriched_dataset_cdf = Enrichment().enrich_polygons(
                    my_local_dataframe,
                    variables=[variable],
                    aggregation=[VariableAggregation(variable, 'SUM')]
                )
    """
    def __init__(self, variable, aggregation=None):
        self.variable = _prepare_variable(variable)
        self.aggregation = aggregation


class VariableFilter(object):
    """This class can be used for filtering the results of
    :py:class:`Enrichment <cartoframes.data.observatory.Enrichment>` functions. It works by appending the
    `VariableFilter` SQL operators to the `WHERE` clause of the resulting enrichment SQL with the `AND` operator.

        Args:
            variable (str or :obj:`Variable`):
                The variable name or :obj:`Variable` instance

            query (str):
                The SQL query filter to be appended to the enrichment SQL query.

        Examples:

            - Equal to number: `VariableFilter(variable, '= 3')`
            - Equal to string: `VariableFilter(variable, "= 'the string'")`
            - Greater that 3: `VariableFilter(variable, '> 3')`

            Next example uses a `VariableFilter` instance to calculate the `SUM` of car-free households
            :obj:`Variable` of the :obj:`Catalog` for each polygon of `my_local_dataframe` pandas `DataFrame` only for
            areas with more than 100 free car-free households

            .. code::

                from cartoframes.data.observatory import Enrichment, Variable, VariableFilter

                variable = Variable.get('no_cars_d19dfd10')
                enriched_dataset_cdf = Enrichment().enrich_polygons(
                    my_local_dataframe,
                    variables=[variable],
                    aggregation=[VariableAggregation(variable, 'SUM')]
                    filters=[VariableFilter(variable, '> 100')]
                )
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
        self.enrichment_id = _ENRICHMENT_ID
        self.geojson_column = _GEOJSON_COLUMN
        self.working_project = _WORKING_PROJECT
        self.public_project = _PUBLIC_PROJECT

    def _execute_enrichment(self, queries, cartodataframe):
        dfs_enriched = list()

        for query in queries:
            df_enriched = self.bq_client.query(query).to_dataframe()
            dfs_enriched.append(df_enriched)

        for df in dfs_enriched:
            cartodataframe = cartodataframe.merge(df, on=self.enrichment_id, how='left')

        # Remove extra columns
        cartodataframe.drop(self.enrichment_id, axis=1, inplace=True)
        cartodataframe.drop(self.geojson_column, axis=1, inplace=True)

        return cartodataframe

    def _prepare_data(self, dataframe, geom_column):
        cartodataframe = CartoDataFrame(dataframe, copy=True, geometry=geom_column)

        # Add extra columns for the enrichment
        cartodataframe[self.enrichment_id] = range(cartodataframe.shape[0])
        cartodataframe[self.geojson_column] = cartodataframe.geometry.apply(to_geojson)

        return cartodataframe

    def _get_temp_table_name(self):
        id_tablename = uuid.uuid4().hex
        return 'temp_{id}'.format(id=id_tablename)

    def _upload_data(self, tablename, cartodataframe):
        bq_dataframe = cartodataframe[[self.enrichment_id, self.geojson_column]]
        schema = {self.enrichment_id: 'INTEGER', self.geojson_column: 'GEOGRAPHY'}

        self.bq_client.upload_dataframe(
            dataframe=bq_dataframe,
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
        geography_id = Dataset.get(variable.dataset).geography
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


def prepare_variables(variables, only_with_agg=False):
    if isinstance(variables, list):
        variables = [_prepare_variable(var, only_with_agg) for var in variables]
    else:
        variables = [_prepare_variable(variables, only_with_agg)]

    return list(filter(None, variables))


def _prepare_variable(variable, only_with_agg=False):
    if isinstance(variable, str):
        variable = Variable.get(variable)

    if not isinstance(variable, Variable):
        raise EnrichmentException("""
            variable should be a `<cartoframes.data.observatory> Variable` instance,
            Variable `id` property or Variable `slug` property
        """)

    if only_with_agg and not variable.agg_method:
        warnings.warn('{} skipped because it does not have aggregation method'.format(variable))
        return None

    _is_available_in_bq(variable)

    return variable


def _is_available_in_bq(variable):
    dataset = Dataset.get(variable.dataset)
    geography = Geography.get(dataset.geography)

    if not (dataset._is_available_in('bq') and geography._is_available_in('bq')):
        raise EnrichmentException("""
            The Dataset or the Geography of the Variable '{}' is not ready for Enrichment.
            Please, contact us for more information.
        """.format(variable.slug))


def get_variable_aggregations(variables, aggregation):
    return [VariableAggregation(variable, __get_aggregation(variable, aggregation)) for variable in variables]


def __get_aggregation(variable, aggregation):
    if aggregation == AGGREGATION_NONE:
        return None
    elif aggregation == AGGREGATION_DEFAULT:
        return variable.agg_method
    elif isinstance(aggregation, str):
        return aggregation
    elif isinstance(aggregation, list):
        agg = variable.agg_method
        for variable_aggregation in aggregation:
            if variable_aggregation.variable == variable:
                agg = variable_aggregation.aggregation
                break
        return agg

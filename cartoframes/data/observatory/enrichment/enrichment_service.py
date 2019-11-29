import uuid

from collections import defaultdict

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

    def _prepare_data(self, dataframe, geom_col):
        cartodataframe = CartoDataFrame(dataframe, copy=True)

        if geom_col:
            cartodataframe.set_geometry(geom_col, inplace=True)

        if not cartodataframe.has_geometry():
            raise EnrichmentException('No valid geometry found. Please provide an input source with ' +
                                      'a valid geometry or specify the "geom_col" param with a geometry column.')

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

    def _get_points_enrichment_sql(self, temp_table_name, variables, filters):
        tables_metadata = self._get_tables_metadata(variables).items()

        return [self._build_points_query(table, metadata, temp_table_name, filters)
                for table, metadata in tables_metadata]

    def _build_points_query(self, table, metadata, temp_table_name, filters):
        variables = ['enrichment_table.{}'.format(variable.column_name) for variable in metadata['variables']]
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        return '''
            SELECT data_table.{enrichment_id}, {variables},
                ST_Area(enrichment_geo_table.geom) AS do_geom_area
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Within(data_table.{geojson_column}, enrichment_geo_table.geom)
            {where};
        '''.format(
            variables=', '.join(variables),
            geojson_column=self.geojson_column,
            enrichment_dataset=enrichment_dataset,
            enrichment_geo_table=enrichment_geo_table,
            enrichment_id=self.enrichment_id,
            where=self._build_where_clausule(filters),
            data_table=data_table,
            table=table
        )

    def _get_polygon_enrichment_sql(self, temp_table_name, variables, filters, aggregation):
        tables_metadata = self._get_tables_metadata(variables).items()

        return [self._build_polygons_query(table, metadata, temp_table_name, filters, aggregation)
                for table, metadata in tables_metadata]

    def _build_polygons_query(self, table, metadata, temp_table_name, filters, aggregation):
        variables = metadata['variables']
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        if aggregation == AGGREGATION_NONE:
            grouper = ''
            variables = self._build_polygons_query_variables_without_aggregation(variables)
        else:
            grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=self.enrichment_id)
            variables = self._build_polygons_query_variables_with_aggregation(variables, aggregation)

        return '''
            SELECT data_table.{enrichment_id}, {variables}
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Intersects(data_table.{geojson_column}, enrichment_geo_table.geom)
            {where}
            {grouper};
        '''.format(
                geojson_column=self.geojson_column,
                enrichment_dataset=enrichment_dataset,
                enrichment_geo_table=enrichment_geo_table,
                enrichment_id=self.enrichment_id,
                where=self._build_where_clausule(filters),
                data_table=data_table,
                grouper=grouper or '',
                variables=variables
            )

    def _build_polygons_query_variables_with_aggregation(self, variables, aggregation):
        return ', '.join([
            self._build_polygons_query_variable_with_aggregation(
                variable,
                aggregation
            ) for variable in variables])

    def _build_polygons_query_variable_with_aggregation(self, variable, aggregation):
        variable_agg = _get_aggregation(variable, aggregation)

        if (variable_agg == 'sum'):
            return """
                {aggregation}(
                    enrichment_table.{column} * (
                        ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geo_column}))
                        /
                        ST_area(data_table.{geo_column})
                    )
                ) AS {aggregation}_{column}
                """.format(
                    column=variable.column_name,
                    geo_column=self.geojson_column,
                    aggregation=variable_agg)
        else:
            return """
                {aggregation}(enrichment_table.{column}) AS {aggregation}_{column}
                """.format(
                    column=variable.column_name,
                    aggregation=variable_agg)

    def _build_polygons_query_variables_without_aggregation(self, variables):
        variables = ['enrichment_table.{}'.format(variable.column_name) for variable in variables]

        return """
            {variables},
            ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geojson_column})) /
            ST_area(data_table.{geojson_column}) AS measures_proportion
            """.format(
                variables=', '.join(variables),
                geojson_column=self.geojson_column)

    def _build_where_clausule(self, filters):
        where = ''
        if len(filters) > 0:
            where_clausules = ["enrichment_table.{} {}".format(f.variable.column_name, f.query) for f in filters]
            where = 'WHERE {}'.format('AND '.join(where_clausules))

        return where


def prepare_variables(variables, credentials, aggregation=None):
    if isinstance(variables, list):
        variables = [_prepare_variable(var, aggregation) for var in variables]
    else:
        variables = [_prepare_variable(variables, aggregation)]

    variables = list(filter(None, variables))

    _validate_bq_operations(variables, credentials)

    return variables


def _prepare_variable(variable, aggregation=None):
    if isinstance(variable, str):
        variable = Variable.get(variable)

    if not isinstance(variable, Variable):
        raise EnrichmentException("""
            variable should be a `<cartoframes.data.observatory> Variable` instance,
            Variable `id` property or Variable `slug` property
        """)

    if aggregation is not None:
        variable_agg = _get_aggregation(variable, aggregation)
        if not variable_agg and aggregation is not AGGREGATION_NONE:
            print('Warning: {} skipped because it does not have aggregation method'.format(variable.id))
            return None

    return variable


def _validate_bq_operations(variables, credentials):
    dataset_ids = list(set([variable.dataset for variable in variables]))

    for dataset_id in dataset_ids:
        dataset = Dataset.get(dataset_id)
        geography = Geography.get(dataset.geography)

        _is_subscribed(dataset, geography, credentials)
        _is_available_in_bq(dataset, geography)


def _is_available_in_bq(dataset, geography):
    if not dataset._is_available_in('bq'):
        raise EnrichmentException("""
            The Dataset '{}' is not ready for Enrichment. Please, contact us for more information.
        """.format(dataset))

    if not geography._is_available_in('bq'):
        raise EnrichmentException("""
            The Geography '{}' is not ready for Enrichment. Please, contact us for more information.
        """.format(geography))


def _is_subscribed(dataset, geography, credentials):
    if not dataset._is_subscribed(credentials):
        raise EnrichmentException("""
            You are not subscribed to the Dataset '{}' yet. Please, use the subscribe method first.
        """.format(dataset))

    if not geography._is_subscribed(credentials):
        raise EnrichmentException("""
            You are not subscribed to the Geography '{}' yet. Please, use the subscribe method first.
        """.format(geography))


def _get_aggregation(variable, aggregation):
    if aggregation in [None, AGGREGATION_NONE]:
        aggregation_method = None
    elif aggregation == AGGREGATION_DEFAULT:
        aggregation_method = variable.agg_method
    elif isinstance(aggregation, str):
        aggregation_method = aggregation
    elif isinstance(aggregation, dict):
        aggregation_method = aggregation.get(variable.id, variable.agg_method)
    else:
        raise ValueError('The `aggregation` parameter is invalid.')

    if aggregation_method is not None:
        return aggregation_method.lower()

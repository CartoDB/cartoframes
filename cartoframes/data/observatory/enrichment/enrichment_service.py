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


class EnrichmentService(object):
    """Base class for the Enrichment utility with commons auxiliary methods"""

    def __init__(self, credentials=None):
        self.credentials = credentials = credentials or get_default_credentials()
        self.user_dataset = self.credentials.get_do_dataset()
        self.bq_client = bigquery_client.BigQueryClient(_WORKING_PROJECT, credentials)
        self.working_project = _WORKING_PROJECT
        self.enrichment_id = _ENRICHMENT_ID
        self.public_project = _PUBLIC_PROJECT
        self.public_dataset = _PUBLIC_DATASET

    def _enrich(self, queries, data, data_geom_column=''):
        data_enriched = self._execute_enrichment(queries, data, data_geom_column)
        data_enriched[data_geom_column] = _compute_geometry_from_geom(data_enriched[data_geom_column])

        return data_enriched

    def _prepare_data(self, data, data_geom_column):
        data_copy = self.__copy_data_and_generate_enrichment_id(data, data_geom_column)
        data_copy[data_geom_column] = data_copy[data_geom_column].apply(wkt_to_geojson)
        return data_copy

    def _get_temp_tablename(self):
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

    def _execute_enrichment(self, queries, data_copy, data_geom_column):
        dfs_enriched = list()

        for query in queries:
            df_enriched = self.bq_client.query(query).to_dataframe()
            dfs_enriched.append(df_enriched)

        for df in dfs_enriched:
            data_copy = data_copy.merge(df, on=self.enrichment_id, how='left')

        data_copy.drop(self.enrichment_id, axis=1, inplace=True)
        data_copy[data_geom_column] = data_copy[data_geom_column].apply(geojson_to_wkt)

        return data_copy

    def _prepare_variables(self, variables, agg_operators=None):
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
            raise EnrichmentException(
                'Variable(s) to enrich should be an instance of Variable / CatalogList / str / list'
            )

        if agg_operators is not None:
            variables_result = [variable for variable in variables_result if variable.agg_method is not None]

        return variables_result

    def _process_filters(self, filters_dict):
        filters = ''
        # TODO: Add data table ref in fields of filters
        if filters_dict:
            filters_list = list()

            for key, value in filters_dict.items():
                filters_list.append('='.join(["{}".format(key), "'{}'".format(value)]))

            filters = ' AND '.join(filters_list)
            filters = 'WHERE {filters}'.format(filters=filters)

        return filters

    def _process_agg_operators(self, agg_operators, variables):
        agg_operators_result = None
        if isinstance(agg_operators, str):
            agg_operators_result = dict()

            for variable in variables:
                agg_operators_result[variable.column_name] = agg_operators

        elif isinstance(agg_operators, dict):
            agg_operators_result = agg_operators.copy()

            for variable in variables:
                if variable.column_name not in agg_operators_result:
                    agg_operators_result[variable.column_name] = variable.agg_method

        return agg_operators_result

    def _get_tables_meta(self, variables):
        tables_meta = defaultdict(defaultdict(list))

        for variable in variables:
            variable_name = variable.column_name
            table_name = self._get_enrichment_table(variable)

            tables_meta[table_name]['variables'].append(variable_name)

            if 'dataset' not in tables_meta[table_name].keys():
                tables_meta[table_name]['dataset'] = self.__get_dataset(variable)

            if 'geotable' not in tables_meta[table_name].keys():
                tables_meta[table_name]['geotable'] = self.__get_geotable(variable)

            if 'project' not in tables_meta[table_name].keys():
                tables_meta[table_name]['project'] = self.__get_project(variable)

        return tables_meta

    def __get_enrichment_table(self, variable):
        enrichment_table = variable.dataset_name

        if variable.project_name != self.public_project:
            enrichment_table = 'view_{dataset}_{table}'.format(
                dataset=variable.schema_name,
                table=variable.dataset_name
            )

        return enrichment_table

    def __get_dataset(self, variable):
        dataset = self.public_dataset
        if variable.project_name != self.public_project:
            dataset = self.user_dataset

        return dataset

    def __get_geotable(self, variable):
        geography_id = CatalogDataset.get(variable.dataset).geography
        _, dataset_geotable, geotable = geography_id.split('.')

        if variable.project_name != self.public_project:
            geotable = 'view_{dataset}_{geotable}'.format(
                dataset=dataset_geotable,
                geotable=geotable
            )

        return geotable

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

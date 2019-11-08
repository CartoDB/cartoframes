import uuid
import logging
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

    def _prepare_variables(self, variables):
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

        return variables_result

    def _process_filters(self, filters_dict):
        filters = ''
        if filters_dict:
            filters_list = list()

            for key, value in filters_dict.items():
                filters_list.append('='.join(["enrichment_table.{}".format(key), "'{}'".format(value)]))

            filters = ' AND '.join(filters_list)
            filters = 'WHERE {filters}'.format(filters=filters)

        return filters

    def _process_agg_operators(self, agg_operators, variables, default_agg):
        agg_operators_result = None
        if isinstance(agg_operators, str):
            agg_operators_result = dict()

            for variable in variables:
                agg_operators_result[variable.column_name] = agg_operators

        elif isinstance(agg_operators, dict):
            agg_operators_result = agg_operators.copy()

        for variable in variables:
            if variable.column_name not in agg_operators_result.keys():
                agg_operators_result[variable.column_name] = variable.agg_method or default_agg
                if not variable.agg_method:
                    logging.warning(
                        "Variable '{}' doesn't have defined agg_method.".format(variable.column_name) +
                        "Default one will be used: '{}' \n".format(default_agg) +
                        "You can change this by using the 'agg_operators' parameter." +
                        "See docs for further details and examples."
                    )

        return agg_operators_result

    def _get_tables_metadata(self, variables):
        tables_metadata = defaultdict(lambda: defaultdict(list))

        for variable in variables:
            table_name = self.__get_enrichment_table(variable)

            tables_metadata[table_name]['variables'].append(variable.column_name)

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

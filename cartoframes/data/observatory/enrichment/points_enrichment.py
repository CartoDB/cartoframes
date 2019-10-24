from __future__ import absolute_import

from .enrichment_service import EnrichmentService


def enrich_points(*args, **kwargs):
    points_enrich = PointsEnrichment(kwargs.get('credentials'))
    return points_enrich.enrich(*args, **kwargs)


class PointsEnrichment(EnrichmentService):

    def __init__(self, credentials=None):
        """
        Enrich a points dataset

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will attempted to be
                used.

        Returns:
            Instance of PointsEnrichment.
        """
        super(PointsEnrichment, self).__init__(credentials)


    def enrich(self, data, variables, data_geom_column='geometry', filters={}, **kwargs):
        """enrich

        This method allows you to enrich your dataset with columns from our data, intersecting
        your points with our geographies. Extra columns as area and population will be provided
        with the aims of normalize these columns.

        Args:
            data (:py:class:`Dataset <cartoframes.data.Dataset>`, DataFrame, GeoDataFrame):
                a Dataset, DataFrame or GeoDataFrame object to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Catalog>`, CatalogList, list, str):
                variable(s), discovered through Catalog, for enriching the `data` argument.
            data_geom_column (str): string indicating the 4326 geometry column in `data`.
            filters (dict, optional): dictionary with either a `column` key
                with the name of the column to filter or a `value` value with the value to filter by.
                Filters will be used using the `AND` operator

        Returns:
            A dataframe as the provided one but with the variables to enrich appended to it

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned dataframe could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a points dataset with Catalog classes:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials
                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = Catalog().country('usa').category('demographics').datasets[0].variables
                dataset_enrich = enrichment.enrich_points(dataset, variables)


            Enrich a points dataset with list of ids:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                dataset_enrich = enrichment.enrich_points(dataset, variables)


            Enrich a points dataset filtering our data:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = Catalog().country('usa').category('demographics').datasets[0].variables
                filters = {'do_date': '2019-09-01'}
                dataset_enrich = enrichment.enrich_points(dataset, variables, filters)
        """
        data_copy = self._prepare_data(data, data_geom_column)

        tablename = self._get_temp_tablename()
        self._upload_dataframe(tablename, data_copy, data_geom_column)

        variables = self.__process_variables(variables, agg_operators)
        queries = self._prepare_points_enrichment_sql(
            tablename, data_geom_column, variables, agg_operators, filters
        )

        return self._enrich(queries, data_copy, data_geom_column)


    def _prepare_points_enrichment_sql(self, tablename, data_geom_column, variables, agg_operators, filters):
        filters_str = self.__process_filters(filters)
        tables_meta_data = self.__get_tables_meta(variables)

        sqls = list()
        for table, table_meta in tables_meta_data.items():
            variables_list = table_meta['variables']
            geotable = table_meta['geotable']
            project = table_meta['project']
            dataset = table_meta['dataset']
            sql = '''
                SELECT data_table.{enrichment_id},
                    {variables},
                    ST_Area(enrichment_geo_table.geom) AS {enrichment_table}_area
                FROM `{project}.{dataset}.{enrichment_table}` enrichment_table
                JOIN `{project}.{dataset}.{enrichment_geo_table}` enrichment_geo_table
                ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{working_project}.{user_dataset}.{data_table}` data_table
                ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
                {filters};
            '''.format(enrichment_id=self.enrichment_id, enrichment_table=table,
                    enrichment_geo_table=geotable, user_dataset=self.user_dataset,
                    working_project=self.working_project, data_table=tablename,
                    data_geom_column=data_geom_column, filters=filters_str,
                    project=project, dataset=dataset,
                    variables=', '.join(['enrichment_table.{}'.format(variable) for variable in variables_list])
            )

            sqls.append(sql)

        return sqls

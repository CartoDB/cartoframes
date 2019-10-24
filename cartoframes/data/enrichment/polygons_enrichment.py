from __future__ import absolute_import

from .enrichment_service import EnrichmentService


def enrich_polygons(*args, **kwargs):
    pol_enrich = PolygonsEnrichment(kwargs.get('credentials'))
    return pol_enrich.enrich(*args, **kwargs)


class PolygonsEnrichment(EnrichmentService):

    def __init__(self, credentials=None):
        """
        Enrich a polygons dataset

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will attempted to be
                used.

        Returns:
            Instance of PolygonsEnrichment.
        """
        super(PointsEnrichment, self).__init__(credentials)


    def enrich(self, data, variables, data_geom_column='geometry', filters={}, agg_operators={}, **kwargs):
        """enrich

        This method allows you to enrich your dataset with columns from our data, intersecting
        your polygons with our geographies. When a polygon intersects with multiple geographies of our
        dataset, the proportional part of the intersection will be used to interpolate the quantity of the
        polygon value intersected, aggregating them with the operator provided by `agg_operators` argument.

        Args:
            data (Dataset, DataFrame, GeoDataFrame): a Dataset, DataFrame or GeoDataFrame object to be enriched.
            variables (Variable, CatalogList, list, str): variable(s), discovered through Catalog,
                for enriching the `data` argument.
            data_geom_column (str): string indicating the 4326 geometry column in `data`.
            filters (dict, optional): dictionary with either a `column` key
                with the name of the column to filter or a `value` value with the value to filter by.
            agg_operators (dict, str, None, optional): dictionary with either a `column` key
                with the name of the column to aggregate or a `operator` value with the operator to group by.
                If `agg_operators`' dictionary is empty (default argument value) then aggregation operators
                will be retrieved from metadata column.
                If `agg_operators` is a string then all columns will be aggregated by this operator.
                If `agg_operators` is `None` then no aggregations will be computed. All the values which
                data geometry intersects with will be returned.

        Returns:
            A dataframe as the provided one but with the variables to enrich appended to it

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned dataframe could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a polygons dataset with Catalog classes and default aggregation methods:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = Catalog().country('usa').category('demographics').datasets[0].variables

                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset with list of ids:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset filtering our data:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = Catalog().country('usa').category('demographics').datasets[0].variables
                filters = {'do_date': '2019-09-01'}

                dataset_enrich = enrichment.enrich_polygons(dataset, variables, filters)


            Enrich a polygons dataset with custom aggregation methods:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                agg_operators = {'in_grades_1_to_4_quantile': 'SUM', 'in_school_quantile': 'AVG'}
                dataset_enrich = enrichment.enrich_polygons(dataset, variables, agg_operators=agg_operators)

            Enrich a polygons dataset with no aggregation methods:

            .. code::

                from data.observatory import enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                agg_operators = None
                dataset_enrich = enrichment.enrich_polygons(dataset, variables, agg_operators=agg_operators)
        """
        data_copy = self._prepare_data(data, data_geom_column)

        tablename = self._get_temp_tablename()
        self._upload_dataframe(tablename, data_copy, data_geom_column)

        queries = self._prepare_polygon_enrichment_sql(
            tablename, data_geom_column, variables, agg_operators, filters
        )

        return self._enrich(queries, data_copy, data_geom_column)


    def _prepare_polygon_enrichment_sql(self, tablename, data_geom_column, variables, agg_operators, filters):
        filters_str = self.__process_filters(filters)
        agg_operators = self.__process_agg_operators(agg_operators, variables)
        table_to_geotable, table_to_variables, table_to_project, table_to_dataset = \
            self.__get_tables_meta(variables)

        grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=self.enrichment_id)

        sqls = list()

        for table, table_meta in tables_meta_data.items():
            variables_list = table_meta['variables']
            geotable = table_meta['geotable']
            project = table_meta['project']
            dataset = table_meta['dataset']

            if agg_operators is not None:
                variables_sql = ['{operator}(enrichment_table.{variable} * \
                                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                                / ST_area(data_table.{data_geom_column}))) as {variable}'.format(variable=variable,
                                data_geom_column=data_geom_column,
                                operator=agg_operators[variable]) for variable in variables_list]

            else:
                variables_sql = ['enrichment_table.{}'.format(variable) for variable in variables] +\
                    ['ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                        / ST_area(data_table.{data_geom_column}) AS measures_proportion'.format(
                            data_geom_column=data_geom_column)]

                grouper = ''

            sql = '''
                SELECT data_table.{enrichment_id}, {variables}
                FROM `{project}.{dataset}.{enrichment_table}` enrichment_table
                    JOIN `{project}.{dataset}.{enrichment_geo_table}` enrichment_geo_table
                        ON enrichment_table.geoid = enrichment_geo_table.geoid
                    JOIN `{working_project}.{user_dataset}.{data_table}` data_table
                        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
                {filters}
                {grouper};
            '''.format(enrichment_id=self.enrichment_id, variables=', '.join(variables_sql),
                    enrichment_table=table, enrichment_geo_table=geotable,
                    user_dataset=self.user_dataset, working_project=self.working_project,
                    data_table=tablename, data_geom_column=data_geom_column,
                    filters=filters_processed, grouper=grouper, project=project,
                    dataset=dataset)

            sqls.append(sql)

        return sqls

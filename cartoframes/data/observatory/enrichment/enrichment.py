from .enrichment_service import EnrichmentService, prepare_variables, process_filters, process_agg_operators

AGGREGATION_DEFAULT = 'default'
AGGREGATION_NONE = 'none'


class AggregateVariable(object):
    def __init__(self, variable, aggregation=None):
        self.variable = variable
        self.aggregation = aggregation


class Enrichment(EnrichmentService):

    def __init__(self, credentials=None):
        """
        Dataset enrichment with `Data Observatory <https://carto.com/platform/location-data-streams/>` data

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will attempted to be
                used.
        """

        super(Enrichment, self).__init__(credentials)

    def enrich_points(self, data, variables, geom_column='geometry', filters={}):
        """Enrich your dataset with columns from our data, intersecting your points with our
        geographies. Extra columns as area and population will be provided with the aims of normalize
        these columns.

        Args:
            data (:py:class:`Dataset <cartoframes.data.Dataset>`, DataFrame, GeoDataFrame):
                a Dataset, DataFrame or GeoDataFrame object to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Catalog>`, CatalogList, list, str):
                variable(s), discovered through Catalog, for enriching the `data` argument.
            geom_column (str): string indicating the 4326 geometry column in `data`.
            filters (dict, optional): dictionary with either a `column` key
                with the name of the column to filter or a `value` value with the value to filter by.
                Filters will be used using the `AND` operator

        Returns:
            A DataFrame as the provided one, but with the variables to enrich appended to it.

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned DataFrame could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a points dataset with Catalog classes:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                catalog = Catalog()
                enrichment = Enrichment()

                variables = catalog.country('usa').category('demographics').datasets[0].variables
                dataset_enrich = enrichment.enrich_points(dataset, variables)


            Enrich a points dataset with list of ids:

            .. code::

                from cartoframes.data.observatory import Enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                enrichment = Enrichment()

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                dataset_enrich = enrichment.enrich_points(dataset, variables)


            Enrich a points dataset filtering our data:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                catalog = Catalog()
                enrichment = Enrichment()

                variables = catalog.country('usa').category('demographics').datasets[0].variables
                filters = {'do_date': '2019-09-01'}
                dataset_enrich = enrichment.enrich_points(dataset, variables, filters)
        """

        variables = prepare_variables(variables)
        data_copy = self._prepare_data(data, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, geom_column)

        queries = self._prepare_points_enrichment_sql(temp_table_name, geom_column, variables, filters)

        return self._execute_enrichment(queries, data_copy, geom_column)

    def enrich_polygons(self, data, variables, geom_column='geometry', filters={}, aggregation=AGGREGATION_DEFAULT):
        """Enrich your dataset with columns from our data, intersecting your polygons with our geographies.
        When a polygon intersects with multiple geographies of our dataset, the proportional part of the
        intersection will be used to interpolate the quantity of the polygon value intersected, aggregating them
        with the operator provided by `agg_operators` argument.

        Args:
            data (Dataset, DataFrame, GeoDataFrame): a Dataset, DataFrame or GeoDataFrame object to be enriched.
            variables (list): list of `<cartoframes.data.observatory> Variable` entities discovered through Catalog to
                enrich your data. To refer to a Variable, You can use a `<cartoframes.data.observatory> Variable`
                instance, the Variable `id` property or the Variable `slug` property. Please, take a look at the
                examples.
            geom_column (str): string indicating the 4326 geometry column in `data`.
            filters (dict, optional): dictionary with either a `column` key with the name of the column to filter
                or a `value` value with the value to filter by.
            aggregation (str, str, list, optional): set the data aggregation. Your polygons can intersect with one or
            more polygons from the DO. With this method you can select how to aggregate the variables data from the
            intersected polygons. Options are:
                - :py:attr:`AGGREGATION_DEFAULT` (default): Every `<cartoframes.data.observatory> Variable` has an
                aggregation method in the Variable `agg_method` property and it will be used to aggregate the data. In
                case it is not defined, `array_agg` function will be used.
                - :py:attr:`AGGREGATION_NONE`: use this option to do the aggregation locally by yourself. you will
                receive an array with all the data from each polygon instersected.
                - list of `<cartoframes.data.observatory> AggregateVariable`: if you want to overwrite some default
                aggregation methods from your selected variables, you can do it using a list of
                `<cartoframes.data.observatory> AggregateVariable`. For example: [AggregateVariable(variable1, 'SUM')]
                - str: if you want to overwrite every default aggregation method, you can pass a string with the
                aggregation method to use.

        Returns:
            A DataFrame as the provided one but with the variables to enrich appended to it

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned DataFrame could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a polygons dataset with Catalog classes and default aggregation methods:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                catalog = Catalog()
                enrichment = Enrichment()

                variables = catalog.country('usa').category('demographics').datasets[0].variables
                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset with list of ids:

            .. code::

                from cartoframes.data.observatory import Enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                enrichment = Enrichment()

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset filtering our data:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                catalog = Catalog()
                enrichment = Enrichment()

                variables = catalog.country('usa').category('demographics').datasets[0].variables
                filters = {'do_date': '2019-09-01'}

                dataset_enrich = enrichment.enrich_polygons(dataset, variables, filters)


            Enrich a polygons dataset with custom aggregation methods:

            .. code::

                from cartoframes.data.observatory import Enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                enrichment = Enrichment()

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                agg_operators = {'in_grades_1_to_4_quantile': 'SUM', 'in_school_quantile': 'AVG'}
                dataset_enrich = enrichment.enrich_polygons(dataset, variables, agg_operators=agg_operators)

            Enrich a polygons dataset with no aggregation methods:

            .. code::

                from cartoframes.data.observatory import Enrichment
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                enrichment = Enrichment()

                variables = [
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_grades_1_to_4_quantile',
                    'carto-do-public-data.acsquantiles.demographics_acsquantiles_usa_schooldistrictelementaryclipped_2015_5yrs_20062010.in_school_quantile'
                ]

                agg_operators = {}
                dataset_enrich = enrichment.enrich_polygons(dataset, variables, agg_operators=agg_operators)
        """

        variables = prepare_variables(variables)
        data_copy = self._prepare_data(data, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, geom_column)

        queries = self._prepare_polygon_enrichment_sql(
            temp_table_name, geom_column, variables, filters, aggregation
        )

        return self._execute_enrichment(queries, data_copy, geom_column)

    def _prepare_points_enrichment_sql(self, temp_table_name, geom_column, variables, filters):
        filters = process_filters(filters)
        tables_metadata = self._get_tables_metadata(variables).items()

        sqls = list()

        for table, metadata in tables_metadata:
            sqls.append(self._build_points_query(table, metadata, temp_table_name, geom_column, filters))

        return sqls

    def _prepare_polygon_enrichment_sql(self, temp_table_name, geom_column, variables, filters, agg_operators):
        filters_str = process_filters(filters)
        agg_operators = process_agg_operators(agg_operators, variables, default_agg='ARRAY_AGG')
        tables_metadata = self._get_tables_metadata(variables).items()

        if agg_operators:
            grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=self.enrichment_id)

        sqls = list()

        for table, metadata in tables_metadata:
            sqls.append(self._build_polygons_query(
                table, metadata, temp_table_name, geom_column, agg_operators, filters_str, grouper)
            )

        return sqls

    def _build_points_query(self, table, metadata, temp_table_name, geom_column, filters):
        variables = ', '.join(
            ['enrichment_table.{}'.format(variable) for variable in metadata['variables']])
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        return '''
            SELECT data_table.{enrichment_id},
                {variables},
                ST_Area(enrichment_geo_table.geom) AS {table}_area
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Within(data_table.{geom_column}, enrichment_geo_table.geom)
            {filters};
        '''.format(
            geom_column=geom_column,
            enrichment_dataset=enrichment_dataset,
            enrichment_geo_table=enrichment_geo_table,
            enrichment_id=self.enrichment_id,
            filters=filters,
            data_table=data_table,
            table=table,
            variables=variables
        )

    def _build_polygons_query(self, table, metadata, temp_table_name, geom_column, agg_operators,
                              filters, grouper):
        variables_list = metadata['variables']
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        variables = self._build_query_variables(agg_operators, variables_list, geom_column)

        return '''
            SELECT data_table.{enrichment_id},
                {variables}
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Intersects(data_table.{geom_column}, enrichment_geo_table.geom)
            {filters}
            {grouper};
        '''.format(
                geom_column=geom_column,
                enrichment_dataset=enrichment_dataset,
                enrichment_geo_table=enrichment_geo_table,
                enrichment_id=self.enrichment_id,
                filters=filters,
                data_table=data_table,
                grouper=grouper or '',
                variables=variables
            )

    def _build_query_variables(self, agg_operators, variables, geom_column):
        sql_variables = []

        if agg_operators is not None:
            sql_variables = ['{operator}(enrichment_table.{variable} * \
                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geom_column}))\
                / ST_area(data_table.{geom_column}))) AS {variable}'.format(
                    variable=variable,
                    geom_column=geom_column,
                    operator=agg_operators.get(variable)) for variable in variables]
        else:
            sql_variables = ['enrichment_table.{}'.format(variable) for variable in variables] + \
                ['ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geom_column}))\
                    / ST_area(data_table.{geom_column}) AS measures_proportion'.format(
                        geom_column=geom_column)]

        return ', '.join(sql_variables)

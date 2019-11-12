from .enrichment_service import EnrichmentService, prepare_variables, process_filters, process_agg_operators


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

    def enrich_points(self, data, variables, data_geom_column='geometry', filters={}, **kwargs):
        """Enrich your dataset with columns from our data, intersecting your points with our
        geographies. Extra columns as area and population will be provided with the aims of normalize
        these columns.

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
        data_copy = self._prepare_data(data, data_geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, data_geom_column)

        queries = self._prepare_points_enrichment_sql(temp_table_name, data_geom_column, variables, filters)

        return self._execute_enrichment(queries, data_copy, data_geom_column)

    def enrich_polygons(self, data, variables, data_geom_column='geometry', filters={}, **kwargs):
        """Enrich your dataset with columns from our data, intersecting your polygons with our geographies.
        When a polygon intersects with multiple geographies of our dataset, the proportional part of the
        intersection will be used to interpolate the quantity of the polygon value intersected, aggregating them
        with the operator provided by `agg_operators` argument.

        Args:
            data (Dataset, DataFrame, GeoDataFrame): a Dataset, DataFrame or GeoDataFrame object to be enriched.
            variables (list): list of `<cartoframes.data.observatory> Variable` entities discovered through Catalog to
                enrich your data. To refer to a Variable, You can use a `<cartoframes.data.observatory> Variable`
                instance, the Variable `id` property or the Variable `slug` property. Please, take a look at the
                examples. Every `<cartoframes.data.observatory> Variable` has an aggregation method in the Variable
                `agg_method` property (in case it is not defined, `array_agg` function will be used). If you want to
                use a different aggregation method for some variable/s, you can do it creating a list for each
                Variable with 2 elements: the Variable and the aggregation method (for example: [Variable, 'SUM']).
                Please, take a look at the examples.
            data_geom_column (str): string indicating the 4326 geometry column in `data`.
            filters (dict, optional): dictionary with either a `column` key
                with the name of the column to filter or a `value` value with the value to filter by.

        Returns:
            A DataFrame as the provided one but with the variables to enrich appended to it

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned DataFrame could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a polygons dataset with one Variable:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials(Credentials.from_file())

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                variables = [variable]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset with all Variables from a Catalog Dataset:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials(Credentials.from_file())

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset with several Variables using their ids:

            .. code::

                from cartoframes.data.observatory import Enrichment
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials(Credentials.from_file())

                enrichment = Enrichment()

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0]
                variable2 = all_variables[1]
                variables = [
                    variable1.id, // you could use the slug too: variable1.slug
                    variable2.id
                ]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(dataset, variables)


            Enrich a polygons dataset filtering our data:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials(Credentials.from_file())

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables
                filters = {'do_date': '2019-09-01'}

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(dataset, variables, filters)


            Enrich a polygons dataset overwriting some of the variables aggregation methods:

            .. code::

                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials(Credentials.from_file())

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM'
                variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
                variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'

                variables = [
                    [variable1, 'SUM'],
                    variable2,           // or [variable2]
                    [variable3, 'AVG']
                ]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(dataset, variables)
        """

        variables = prepare_variables(variables)
        data_copy = self._prepare_data(data, data_geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, data_geom_column)

        queries = self._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        return self._execute_enrichment(queries, data_copy, data_geom_column)

    def _prepare_points_enrichment_sql(self, temp_table_name, data_geom_column, variables, filters):
        filters = process_filters(filters)
        tables_metadata = self._get_tables_metadata(variables).items()

        sqls = list()

        for table, metadata in tables_metadata:
            sqls.append(self._build_points_query(table, metadata, temp_table_name, data_geom_column, filters))

        return sqls

    def _prepare_polygon_enrichment_sql(self, temp_table_name, data_geom_column, variables, filters, agg_operators):
        filters_str = process_filters(filters)
        agg_operators = process_agg_operators(agg_operators, variables, default_agg='ARRAY_AGG')
        tables_metadata = self._get_tables_metadata(variables).items()

        if agg_operators:
            grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=self.enrichment_id)

        sqls = list()

        for table, metadata in tables_metadata:
            sqls.append(self._build_polygons_query(
                table, metadata, temp_table_name, data_geom_column, agg_operators, filters_str, grouper)
            )

        return sqls

    def _build_points_query(self, table, metadata, temp_table_name, data_geom_column, filters):
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
                    ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            {filters};
        '''.format(
            data_geom_column=data_geom_column,
            enrichment_dataset=enrichment_dataset,
            enrichment_geo_table=enrichment_geo_table,
            enrichment_id=self.enrichment_id,
            filters=filters,
            data_table=data_table,
            table=table,
            variables=variables
        )

    def _build_polygons_query(self, table, metadata, temp_table_name, data_geom_column, agg_operators,
                              filters, grouper):
        variables_list = metadata['variables']
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        variables = self._build_query_variables(agg_operators, variables_list, data_geom_column)

        return '''
            SELECT data_table.{enrichment_id},
                {variables}
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
            {filters}
            {grouper};
        '''.format(
                data_geom_column=data_geom_column,
                enrichment_dataset=enrichment_dataset,
                enrichment_geo_table=enrichment_geo_table,
                enrichment_id=self.enrichment_id,
                filters=filters,
                data_table=data_table,
                grouper=grouper or '',
                variables=variables
            )

    def _build_query_variables(self, agg_operators, variables, data_geom_column):
        sql_variables = []

        if agg_operators is not None:
            sql_variables = ['{operator}(enrichment_table.{variable} * \
                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                / ST_area(data_table.{data_geom_column}))) AS {variable}'.format(
                    variable=variable,
                    data_geom_column=data_geom_column,
                    operator=agg_operators.get(variable)) for variable in variables]
        else:
            sql_variables = ['enrichment_table.{}'.format(variable) for variable in variables] + \
                ['ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                    / ST_area(data_table.{data_geom_column}) AS measures_proportion'.format(
                        data_geom_column=data_geom_column)]

        return ', '.join(sql_variables)

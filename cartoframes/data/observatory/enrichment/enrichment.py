from .enrichment_service import EnrichmentService, prepare_variables, get_variable_aggregations, \
    AGGREGATION_DEFAULT, AGGREGATION_NONE


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
            filters (list, optional): list of `<cartoframes.data.observatory> VariableFilter` to filter rows from
                the enrichment data. Example: [VariableFilter(variable1, "= 'a string'")]

        Returns:
            A DataFrame as the provided one, but with the variables to enrich appended to it.

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned DataFrame could be different
            than the `data` argument number of rows.

        Examples:

            Enrich a points dataset with Catalog classes:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_points(df, variables)


            Enrich a points dataset with several Variables using their ids:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0]
                variable2 = all_variables[1]
                variables = [
                    variable1.id,
                    variable2.id
                ]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_points(df, variables)


            Enrich a points dataset with filters:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog, VariableFilter
                from cartoframes.auth import set_default_credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                filter = VariableFilter(variable, '=', '2019-09-01')

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_points(df, variables=[variable], filters=[filter])

        """

        variables = prepare_variables(variables)
        data_copy = self._prepare_data(data, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, geom_column)

        queries = self._get_points_enrichment_sql(temp_table_name, geom_column, variables, filters)

        return self._execute_enrichment(queries, data_copy, geom_column)

    AGGREGATION_DEFAULT = AGGREGATION_DEFAULT
    """Use default aggregation method for polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    AGGREGATION_NONE = AGGREGATION_NONE
    """Do not aggregate data in polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    def enrich_polygons(self, data, variables, geom_column='geometry', filters=[], aggregation=AGGREGATION_DEFAULT):
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
            filters (list, optional): list of `<cartoframes.data.observatory> VariableFilter` to filter rows from
                the enrichment data. Example: [VariableFilter(variable1, "= 'a string'")]
            aggregation (str, str, list, optional): set the data aggregation. Your polygons can intersect with one or
            more polygons from the DO. With this method you can select how to aggregate the variables data from the
            intersected polygons. Options are:
                - :py:attr:`Enrichment.AGGREGATION_DEFAULT` (default): Every `<cartoframes.data.observatory> Variable`
                has an aggregation method in the Variable `agg_method` property and it will be used to aggregate the
                data. In case it is not defined, `array_agg` function will be used.
                - :py:attr:`Enrichment.AGGREGATION_NONE`: use this option to do the aggregation locally by yourself.
                you will receive an array with all the data from each polygon instersected.
                - list of `<cartoframes.data.observatory> VariableAggregation`: if you want to overwrite some default
                aggregation methods from your selected variables, you can do it using a list of
                `<cartoframes.data.observatory> VariableAggregation`. Example: [VariableAggregation(variable, 'SUM')]
                - str: if you want to overwrite every default aggregation method, you can pass a string with the
                aggregation method to use.

        Returns:
            A DataFrame as the provided one but with the variables to enrich appended to it

            Note that if the geometry of the `data` you provide intersects with more than one geometry
            in the enrichment dataset, the number of rows of the returned DataFrame could be different
            than the `data` argument number of rows.


        Examples:

            Enrich a polygons dataset with one Variable:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                variables = [variable]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataset with all Variables from a Catalog Dataset:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataset with several Variables using their ids:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0]
                variable2 = all_variables[1]
                variables = [
                    variable1.id,
                    variable2.id
                ]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataset with filters:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog, VariableFilter
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                filter = VariableFilter(variable, '=', '2019-09-01')

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(df, variables=[variable], filters=[filter])


            Enrich a polygons dataset overwriting some of the variables aggregation methods:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog, VariableAggregation
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM'
                variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
                variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'

                variables = [variable1, variable2, variable3]

                aggregations = [
                    VariableAggregation(variable1, 'SUM'),
                    VariableAggregation(variable3, 'AVG')
                ]

                enrichment = Enrichment()
                dataset_enrich = enrichment.enrich_polygons(df, variables, aggregations=aggregations)
        """

        variables = prepare_variables(variables)
        data_copy = self._prepare_data(data, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_dataframe(temp_table_name, data_copy, geom_column)

        queries = self._get_polygon_enrichment_sql(
            temp_table_name, geom_column, variables, filters, aggregation
        )

        return self._execute_enrichment(queries, data_copy, geom_column)

    def _get_points_enrichment_sql(self, temp_table_name, geom_column, variables, filters):
        tables_metadata = self._get_tables_metadata(variables).items()

        return [self._build_points_query(table, metadata, temp_table_name, geom_column, filters)
                for table, metadata in tables_metadata]

    def _build_points_query(self, table, metadata, temp_table_name, geom_column, filters):
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
                ST_Area(enrichment_geo_table.geom) AS {table}_area
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Within(data_table.{geom_column}, enrichment_geo_table.geom)
            {where};
        '''.format(
            variables=', '.join(variables),
            geom_column=geom_column,
            enrichment_dataset=enrichment_dataset,
            enrichment_geo_table=enrichment_geo_table,
            enrichment_id=self.enrichment_id,
            where=self._build_where_clausule(filters),
            data_table=data_table,
            table=table
        )

    def _get_polygon_enrichment_sql(self, temp_table_name, geom_column, variables, filters, aggregation):
        variable_aggregations = get_variable_aggregations(variables, aggregation)
        tables_metadata = self._get_tables_metadata(variable_aggregations).items()

        return [self._build_polygons_query(table, metadata, temp_table_name, geom_column, filters, aggregation)
                for table, metadata in tables_metadata]

    def _build_polygons_query(self, table, metadata, temp_table_name, geom_column, filters, aggregation):
        variable_aggregations = metadata['variables']
        enrichment_dataset = metadata['dataset']
        enrichment_geo_table = metadata['geo_table']
        data_table = '{project}.{user_dataset}.{temp_table_name}'.format(
            project=self.working_project,
            user_dataset=self.user_dataset,
            temp_table_name=temp_table_name
        )

        if aggregation == AGGREGATION_NONE:
            grouper = ''
            variables = self._build_polygons_query_variables_without_aggregation(variable_aggregations, geom_column)
        else:
            grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=self.enrichment_id)
            variables = self._build_polygons_query_variables_with_aggregation(variable_aggregations, geom_column)

        return '''
            SELECT data_table.{enrichment_id}, {variables}
            FROM `{enrichment_dataset}` enrichment_table
                JOIN `{enrichment_geo_table}` enrichment_geo_table
                    ON enrichment_table.geoid = enrichment_geo_table.geoid
                JOIN `{data_table}` data_table
                    ON ST_Intersects(data_table.{geom_column}, enrichment_geo_table.geom)
            {where}
            {grouper};
        '''.format(
                geom_column=geom_column,
                enrichment_dataset=enrichment_dataset,
                enrichment_geo_table=enrichment_geo_table,
                enrichment_id=self.enrichment_id,
                where=self._build_where_clausule(filters),
                data_table=data_table,
                grouper=grouper or '',
                variables=variables
            )

    def _build_polygons_query_variables_with_aggregation(self, variable_aggregations, geom_column):
        return ', '.join(["""
            {operator}(enrichment_table.{variable} *
            (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geom_column}))
            / ST_area(data_table.{geom_column}))) AS {variable}
            """.format(
                variable=variable_aggregation.variable.column_name,
                geom_column=geom_column,
                operator=variable_aggregation.aggregation) for variable_aggregation in variable_aggregations])

    def _build_polygons_query_variables_without_aggregation(self, variable_aggregations, geom_column):
        variables = ['enrichment_table.{}'.format(variable_aggregation.variable.column_name)
                     for variable_aggregation in variable_aggregations]

        return """
            {variables},
            ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geom_column})) /
            ST_area(data_table.{geom_column}) AS measures_proportion
            """.format(
                variables=', '.join(variables),
                geom_column=geom_column)

    def _build_where_clausule(self, filters):
        where = ''
        if len(filters) > 0:
            where_clausules = ["enrichment_table.{} {}".format(f.variable.column_name, f.query) for f in filters]
            where = 'WHERE {}'.format('AND '.join(where_clausules))

        return where

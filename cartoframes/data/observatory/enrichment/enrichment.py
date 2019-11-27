from .enrichment_service import EnrichmentService, prepare_variables, \
    AGGREGATION_DEFAULT, AGGREGATION_NONE, _get_aggregation


class Enrichment(EnrichmentService):
    """This is the main class to enrich your own data with data from the
    `Data Observatory <https://carto.com/platform/location-data-streams/>`__

    To be able to use the `Enrichment` functions you need A CARTO account with Data Observatory v2 enabled. Contact
    us at support@carto.com for more information about this.

    Please, see the :obj:`Catalog` discovery and subscription guides, to understand how to explore the Data Observatory
    repository and subscribe to premium datasets to be used in your enrichment workflows.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            credentials of user account. If not provided,
            a default credentials (if set with :py:meth:`set_default_credentials
            <cartoframes.auth.set_default_credentials>`) will attempted to be
            used.
    """

    def __init__(self, credentials=None):
        super(Enrichment, self).__init__(credentials)

    def enrich_points(self, dataframe, variables, geom_column='geometry', filters={}):
        """Enrich your points `DataFrame` with columns (:obj:`Variable`) from one or more :obj:`Dataset`
        in the Data Observatory, intersecting the points in the source `DataFrame` with the geographies in the
        Data Observatory.

        Extra columns as `area` and `population` will be provided in the resulting `DataFrame` for normalization
        purposes.

        Args:
            dataframe (pandas `DataFrame`, geopandas `GeoDataFrame`
                or :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`): a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`.
            geom_column (str): string indicating the 4326 geometry column name in the
                source `DataFrame`. Defaults to `geometry`.
            filters (list, optional): list of :obj:`VariableFilter` to filter rows from
                the enrichment data. Example: `[VariableFilter(variable1, "= 'a string'")]`

        Returns:
            A :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>` enriched with the variables passed as argument.

        *Note that if the points of the `dataframe` you provide are contained in more than one geometry
        in the enrichment dataset, the number of rows of the returned `CartoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:

            Enrich a points `DataFrame` with Catalog classes:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_points(df, variables)


            Enrich a points dataframe with several Variables using their ids:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog

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
                cdf_enrich = enrichment.enrich_points(df, variables)


            Enrich a points dataframe with filters:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog, VariableFilter

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                filter = VariableFilter(variable, "= '2019-09-01'")

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_points(df, variables=[variable], filters=[filter])
        """
        variables = prepare_variables(variables)
        cartodataframe = self._prepare_data(dataframe, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_points_enrichment_sql(temp_table_name, variables, filters)
        return self._execute_enrichment(queries, cartodataframe)

    AGGREGATION_DEFAULT = AGGREGATION_DEFAULT
    """Use default aggregation method for polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    AGGREGATION_NONE = AGGREGATION_NONE
    """Do not aggregate data in polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    def enrich_polygons(self, dataframe, variables, geom_column='geometry', filters=[],
                        aggregation=AGGREGATION_DEFAULT):
        """Enrich your polygons `DataFrame` with columns (:obj:`Variable`) from one or more :obj:`Dataset` in
        the Data Observatory by intersecting the polygons in the source `DataFrame` with geographies in the
        Data Observatory.

        When a polygon intersects with multiple geographies, the proportional part of the intersection will be used
        to interpolate the quantity of the polygon value intersected, aggregating them. Most of `Variable` instances
        have a `agg_operator` property what is used by default as aggregation function, but you can overwrite it
        using the `aggregation` parameter (not even doing the aggregation). If a variable do not have the
        `agg_operator` property set and you do not overwrite it either (with the `aggregation` parameter), the
        variable column will be skipped from the enrichment.

        Args:
            dataframe (pandas `DataFrame`, geopandas `GeoDataFrame`
                or :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`): a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`.
            geom_column (str): string indicating the 4326 geometry column name in the source `DataFrame`.
                Defaults to `geometry`.
            filters (list, optional): list of :obj:`VariableFilter` to filter rows from
                the enrichment data. Example: `[VariableFilter(variable1, "= 'a string'")]`
            aggregation (str, list, optional): sets the data aggregation. The polygons in the source `DataFrame` can
                intersect with one or more polygons from the Data Observatory. With this method you can select how to
                aggregate the resulting data.

                A aggregation method can be one of these values: 'MIN', 'MAX', 'SUM', 'AVG', 'COUNT',
                'ARRAY_AGG', 'ARRAY_CONCAT_AGG', 'STRING_AGG' but check this
                `documentation <https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions>`__
                for a complete list of aggregate functions.

                The options are:
                    - :py:attr:`Enrichment.AGGREGATION_DEFAULT` (default): Every :obj:`Variable` has a default
                    aggregation method in the Variable `agg_method` property and it will be used to aggregate the data
                    (a variable could not have `agg_method` defined and in this case, the variables will be skipped).
                    - :py:attr:`Enrichment.AGGREGATION_NONE`: use this option to do the aggregation locally by yourself.
                    you will receive an array with all the data from each polygon instersected.
                    - str: if you want to overwrite every default aggregation method, you can pass a string with the
                    aggregation method to use.
                    - dictionary: if you want to overwrite some default aggregation methods from your selected
                    variables, use a dict as
                    :py:class:`Variable <cartoframes.data.observatory.Variable>`.id: aggregation method pairs,
                    for example: `{variable1.id: 'SUM', variable3.id: 'AVG'}`.

        Returns:
            A :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>` enriched with the variables passed as argument.

        *Note that if the geometry of the `dataframe` you provide intersects with more than one geometry
        in the enrichment dataset, the number of rows of the returned `CartoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:

            Enrich a polygons dataframe with one Variable:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                variables = [variable]

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataframe with all Variables from a Catalog Dataset:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variables = catalog.country('usa').category('demographics').datasets[0].variables

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataframe with several Variables using their ids:

            .. code::

                import pandas
                from cartoframes.auth import set_default_credentials
                from cartoframes.data.observatory import Enrichment, Catalog

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
                cdf_enrich = enrichment.enrich_polygons(df, variables)


            Enrich a polygons dataframe with filters:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog, VariableFilter
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                variable = catalog.country('usa').category('demographics').datasets[0].variables[0]
                filter = VariableFilter(variable, "= '2019-09-01'")

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_polygons(df, variables=[variable], filters=[filter])


            Enrich a polygons dataframe overwriting every variables aggregation methods to use `SUM` function:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM'
                variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
                variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'

                variables = [variable1, variable2, variable3]

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_polygons(df, variables, aggregation='SUM')

            Enrich a polygons dataframe overwriting some of the variables aggregation methods:

            .. code::

                import pandas
                from cartoframes.data.observatory import Enrichment, Catalog
                from cartoframes.auth import set_default_credentials, Credentials

                set_default_credentials()

                df = pandas.read_csv('...')

                catalog = Catalog()
                all_variables = catalog.country('usa').category('demographics').datasets[0].variables
                variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM'
                variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
                variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'

                variables = [variable1, variable2, variable3]

                aggregation = {
                    variable1.id: 'SUM',
                    variable3.id: 'AVG'
                }

                enrichment = Enrichment()
                cdf_enrich = enrichment.enrich_polygons(df, variables, aggregation=aggregation)
        """

        variables = prepare_variables(variables, aggregation)
        cartodataframe = self._prepare_data(dataframe, geom_column)

        temp_table_name = self._get_temp_table_name()
        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_polygon_enrichment_sql(temp_table_name, variables, filters, aggregation)
        return self._execute_enrichment(queries, cartodataframe)

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
                ST_Area(enrichment_geo_table.geom) AS {table}_area
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

        if (variable_agg == 'SUM'):
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
                {aggregation}(
                    enrichment_table.{column} * (
                        ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geo_column}))
                    )
                ) AS {aggregation}_{column}
                """.format(
                    column=variable.column_name,
                    geo_column=self.geojson_column,
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

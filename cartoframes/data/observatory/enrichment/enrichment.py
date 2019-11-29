from .enrichment_service import EnrichmentService, prepare_variables, AGGREGATION_DEFAULT, AGGREGATION_NONE


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

    def enrich_points(self, dataframe, variables, geom_col=None, filters=[]):
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
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
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
        variables = prepare_variables(variables, self.credentials)
        cartodataframe = self._prepare_data(dataframe, geom_col)

        temp_table_name = self._get_temp_table_name()
        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_points_enrichment_sql(temp_table_name, variables, filters)
        return self._execute_enrichment(queries, cartodataframe)

    AGGREGATION_DEFAULT = AGGREGATION_DEFAULT
    """Use default aggregation method for polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    AGGREGATION_NONE = AGGREGATION_NONE
    """Do not aggregate data in polygons enrichment. More info in :py:attr:`Enrichment.enrich_polygons`"""

    def enrich_polygons(self, dataframe, variables, geom_col=None, filters=[], aggregation=AGGREGATION_DEFAULT):
        """Enrich your polygons `DataFrame` with columns (:obj:`Variable`) from one or more :obj:`Dataset` in
        the Data Observatory by intersecting the polygons in the source `DataFrame` with geographies in the
        Data Observatory.

        When a polygon intersects with multiple geographies, the proportional part of the intersection will be used
        to interpolate the quantity of the polygon value intersected, aggregating them. Most of :obj:`Variable`
        instances have a :py:attr:`Variable.agg_method` property which is used by default as aggregation function, but
        you can overwrite it using the `aggregation` parameter (not even doing the aggregation). If a variable does not
        have the `agg_method` property set and you do not overwrite it either (with the `aggregation` parameter), the
        variable column will be skipped from the enrichment.

        Args:
            dataframe (pandas `DataFrame`, geopandas `GeoDataFrame`
                or :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`): a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
            filters (list, optional): list of :obj:`VariableFilter` to filter rows from
                the enrichment data. Example: `[VariableFilter(variable1, "= 'a string'")]`
            aggregation (str, list, optional): sets the data aggregation. The polygons in the source `DataFrame` can
                intersect with one or more polygons from the Data Observatory. With this method you can select how to
                aggregate the resulting data.

                An aggregation method can be one of these values: 'MIN', 'MAX', 'SUM', 'AVG', 'COUNT',
                'ARRAY_AGG', 'ARRAY_CONCAT_AGG', 'STRING_AGG' but check this
                `documentation <https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions>`__
                for a complete list of aggregate functions.

                The options are:
                    - :py:attr:`Enrichment.AGGREGATION_DEFAULT` (default): Every :obj:`Variable` has a default
                    aggregation method in the :py:attr:`Variable.agg_method` property and it will be used to
                    aggregate the data (a variable could not have `agg_method` defined and in this case, the
                    variables will be skipped).

                    - :py:attr:`Enrichment.AGGREGATION_NONE`: use this option to do the aggregation locally by yourself.
                    You will receive a row of data from each polygon instersected.

                    - str: if you want to overwrite every default aggregation method, you can pass a string with the
                    aggregation method to use.

                    - dictionary: if you want to overwrite some default aggregation methods from your selected
                    variables, use a dict as :py:attr:`Variable.id`: aggregation method pairs, for example:
                    `{variable1.id: 'SUM', variable3.id: 'AVG'}`.

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
        variables = prepare_variables(variables, self.credentials, aggregation)
        cartodataframe = self._prepare_data(dataframe, geom_col)

        temp_table_name = self._get_temp_table_name()
        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_polygon_enrichment_sql(temp_table_name, variables, filters, aggregation)
        return self._execute_enrichment(queries, cartodataframe)

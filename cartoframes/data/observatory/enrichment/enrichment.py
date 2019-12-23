from .enrichment_service import EnrichmentService, prepare_variables, AGGREGATION_DEFAULT
from ....utils.utils import timelogger


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

    def enrich_points(self, dataframe, variables, geom_col=None, filters={}):
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
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`. The maximum number of
                variables is 50.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
            filters (dict, optional): dictionary to filter results by variable values. As a key it receives the
                variable id, and as value receives a SQL operator, for example: {variable1.id: "> 30"}. It works by
                appending the filter SQL operators to the `WHERE` clause of the resulting enrichment SQL with the `AND`
                operator (in the example: `WHERE {variable1.column_name} > 30`). The variables used to filter results
                should exists in `variables` property list.

        Returns:
            A :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>` enriched with the variables passed as argument.

        Raises:
            EnrichmentError: if there is an error in the enrichment process.

        *Note that if the points of the `dataframe` you provide are contained in more than one geometry
        in the enrichment dataset, the number of rows of the returned `CartoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:
            Enrich a points `DataFrame` with Catalog classes:

            >>> df = pandas.read_csv('...')
            >>> variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> cdf_enrich = Enrichment().enrich_points(df, variables)

            Enrich a points dataframe with several Variables using their ids:

            >>> df = pandas.read_csv('...')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:2]
            >>> cdf_enrich = Enrichment().enrich_points(df, variables)

            Enrich a points dataframe with filters:

            >>> df = pandas.read_csv('...')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> filters = {variable.id: "= '2019-09-01'"}
            >>> cdf_enrich = Enrichment().enrich_points(df, variables=[variable], filters=filters)

        """
        variables = prepare_variables(variables, self.credentials)
        cartodataframe = self._prepare_data(dataframe, geom_col)

        temp_table_name = self._get_temp_table_name()
        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_points_enrichment_sql(temp_table_name, variables, filters)
        return self._execute_enrichment(queries, cartodataframe)

    @timelogger
    def enrich_polygons(self, dataframe, variables, geom_col=None, filters={}, aggregation=AGGREGATION_DEFAULT):
        """Enrich your polygons `DataFrame` with columns (:obj:`Variable`) from one or more :obj:`Dataset` in
        the Data Observatory by intersecting the polygons in the source `DataFrame` with geographies in the
        Data Observatory.

        When a polygon intersects with multiple geographies, the proportional part of the intersection will be used
        to interpolate the quantity of the polygon value intersected, aggregating them. Most of :obj:`Variable`
        instances have a :py:attr:`Variable.agg_method` property which is used by default as an aggregation function,
        but you can overwrite it using the `aggregation` parameter (not even doing the aggregation). If a variable does
        not have the `agg_method` property set and you do not overwrite it (with the `aggregation` parameter), the
        variable column will be skipped from the enrichment.

        Args:
            dataframe (pandas `DataFrame`, geopandas `GeoDataFrame`
                or :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`): a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`. The maximum number of
                variables is 50.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
            filters (dict, optional): dictionary to filter results by variable values. As a key it receives the
                variable id, and as value receives a SQL operator, for example: {variable1.id: "> 30"}. It works by
                appending the filter SQL operators to the `WHERE` clause of the resulting enrichment SQL with the `AND`
                operator (in the example: `WHERE {variable1.column_name} > 30`). The variables used to filter results
                should exists in `variables` property list.
            aggregation (None, str, list, optional): sets the data aggregation. The polygons in the source `DataFrame`
                can intersect with one or more polygons from the Data Observatory. With this method you can select how
                to aggregate the resulting data.

                An aggregation method can be one of these values: 'MIN', 'MAX', 'SUM', 'AVG', 'COUNT',
                'ARRAY_AGG', 'ARRAY_CONCAT_AGG', 'STRING_AGG' but check this
                `documentation <https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions>`__
                for a complete list of aggregate functions.

                The options are:
                - str (default): 'default'. Most :obj:`Variable`s has a default
                aggregation method in the :py:attr:`Variable.agg_method` property and it will be used to
                aggregate the data (a variable could not have `agg_method` defined and in this case, the
                variable will be skipped).
                - `None`: use this option to do the aggregation locally by yourself.
                You will receive a row of data from each polygon intersected. Also, you will receive the areas of the
                polygons intersection and the polygons intersected.
                - str: if you want to overwrite every default aggregation method, you can pass a string with the
                aggregation method to use.
                - dictionary: if you want to overwrite some default aggregation methods from your selected
                variables, use a dict as :py:attr:`Variable.id`: aggregation method pairs, for example:
                `{variable1.id: 'SUM', variable3.id: 'AVG'}`.

        Returns:
            A :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>` enriched with the variables passed as argument.

        Raises:
            EnrichmentError: if there is an error in the enrichment process.

        *Note that if the geometry of the `dataframe` you provide intersects with more than one geometry
        in the enrichment dataset, the number of rows of the returned `CartoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:
            Enrich a polygons dataframe with one Variable:

            >>> df = pandas.read_csv('...')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> variables = [variable]
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables)

            Enrich a polygons dataframe with all Variables from a Catalog Dataset:

            >>> df = pandas.read_csv('...')
            >>> variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables)

            Enrich a polygons dataframe with several Variables using their ids:

            >>> df = pandas.read_csv('...')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:2]
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables)

            Enrich a polygons dataframe with filters:

            >>> df = pandas.read_csv('...')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> filters = {variable.id: "= '2019-09-01'"}
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables=[variable], filters=filters)

            Enrich a polygons dataframe overwriting every variables aggregation method to use `SUM` function:

            >>> df = pandas.read_csv('...')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:3]
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables, aggregation='SUM')

            Enrich a polygons dataframe overwriting some of the variables aggregation methods:

            >>> df = pandas.read_csv('...')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:3]
            >>> aggregation = {
            ...     variable1.id: 'SUM',
            ...     variable3.id: 'AVG'
            >>> }
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables, aggregation=aggregation)

            Enrich a polygons dataframe without aggregating variables (because you want to it yourself, for example,
                in case you want to use your custom function for aggregating the data):

            >>> df = pandas.read_csv('...')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:3]
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables, aggregation=None)

            The next example uses filters to calculate the `SUM` of car-free households
            :obj:`Variable` of the :obj:`Catalog` for each polygon of `my_local_dataframe` pandas `DataFrame` only for
            areas with more than 100 car-free households:

            >>> variable = Variable.get('no_cars_d19dfd10')
            >>> enriched_dataset_cdf = Enrichment().enrich_polygons(
            ...     my_local_dataframe,
            ...     variables=[variable],
            ...     aggregation={variable.id: 'SUM'}
            ...     filters={variable.id: '> 100'}
            >>> )

        """
        variables = prepare_variables(variables, self.credentials, aggregation)

        cartodataframe = self._prepare_data(dataframe, geom_col)
        temp_table_name = self._get_temp_table_name()

        self._upload_data(temp_table_name, cartodataframe)

        queries = self._get_polygon_enrichment_sql(temp_table_name, variables, filters, aggregation)
        return self._execute_enrichment(queries, cartodataframe)

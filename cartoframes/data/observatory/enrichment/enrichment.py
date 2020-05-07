from .enrichment_service import EnrichmentService, AGGREGATION_DEFAULT

GEOM_TYPE_POINTS = 'points'
GEOM_TYPE_POLYGONS = 'polygons'


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

    def enrich_points(self, dataframe, variables, geom_col=None, filters=None):
        """Enrich your points `DataFrame` with columns (:obj:`Variable`) from one or more :obj:`Dataset`
        in the Data Observatory, intersecting the points in the source `DataFrame` with the geographies in the
        Data Observatory.

        Extra columns as `area` and `population` will be provided in the resulting `DataFrame` for normalization
        purposes.

        Args:
            dataframe (pandas.DataFrame, geopandas.GeoDataFrame: a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
            filters (dict, optional): dictionary to filter results by variable values. As a key it receives the
                variable id, and as value receives a SQL operator, for example: `{variable1.id: "> 30"}`. It works by
                appending the filter SQL operators to the `WHERE` clause of the resulting enrichment SQL with the `AND`
                operator (in the example: `WHERE {variable1.column_name} > 30`). If you want to filter the same
                variable several times you can use a list as a dict value: `{variable1.id: ["> 30", "< 100"]}`. The
                variables used to filter results should exist in `variables` property list.

        Returns:
            A geopandas.GeoDataFrame enriched with the variables passed as argument.

        Raises:
            EnrichmentError: if there is an error in the enrichment process.

        *Note that if the points of the `dataframe` you provide are contained in more than one geometry
        in the enrichment dataset, the number of rows of the returned `GeoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:
            Enrich a points `DataFrame` with Catalog classes:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> gdf_enrich = Enrichment().enrich_points(df, variables, geom_col='the_geom')

            Enrich a points dataframe with several Variables using their ids:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:2]
            >>> gdf_enrich = Enrichment().enrich_points(df, variables, geom_col='the_geom')

            Enrich a points dataframe with filters:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> filters = {variable.id: "= '2019-09-01'"}
            >>> gdf_enrich = Enrichment().enrich_points(
            ...     df,
            ...     variables=[variable],
            ...     filters=filters,
            ...     geom_col='the_geom')

        """
        return self._enrich(GEOM_TYPE_POINTS, dataframe, variables, geom_col, filters)

    def enrich_polygons(self, dataframe, variables, geom_col=None, filters=None, aggregation=AGGREGATION_DEFAULT):
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
            dataframe (pandas.DataFrame, geopandas.GeoDataFrame): a `DataFrame` instance to be enriched.
            variables (:py:class:`Variable <cartoframes.data.observatory.Variable>`, list, str):
                variable ID, slug or :obj:`Variable` instance or list of variable IDs, slugs
                or :obj:`Variable` instances taken from the Data Observatory :obj:`Catalog`.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.
            filters (dict, optional): dictionary to filter results by variable values. As a key it receives the
                variable id, and as value receives a SQL operator, for example: `{variable1.id: "> 30"}`. It works by
                appending the filter SQL operators to the `WHERE` clause of the resulting enrichment SQL with the `AND`
                operator (in the example: `WHERE {variable1.column_name} > 30`). If you want to filter the same
                variable several times you can use a list as a dict value: `{variable1.id: ["> 30", "< 100"]}`. The
                variables used to filter results should exist in `variables` property list.
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
                `{variable1.id: 'SUM', variable3.id: 'AVG'}`. Or if you want to use several aggregation method for one
                variable, you can use a list as a dict value: `{variable1.id: ['SUM', 'AVG'], variable3.id: 'AVG'}`

        Returns:
            A geopandas.GeoDataFrame enriched with the variables passed as argument.

        Raises:
            EnrichmentError: if there is an error in the enrichment process.

        *Note that if the geometry of the `dataframe` you provide intersects with more than one geometry
        in the enrichment dataset, the number of rows of the returned `GeoDataFrame` could be different
        than the `dataframe` argument number of rows.*

        Examples:
            Enrich a polygons dataframe with one Variable:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> variables = [variable]
            >>> gdf_enrich = Enrichment().enrich_polygons(df, variables, geom_col='the_geom')

            Enrich a polygons dataframe with all Variables from a Catalog Dataset:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> gdf_enrich = Enrichment().enrich_polygons(df, variables, geom_col='the_geom')

            Enrich a polygons dataframe with several Variables using their ids:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = [all_variables[0].id, all_variables[1].id]
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables, geom_col='the_geom')

            Enrich a polygons dataframe with filters:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> variable = Catalog().country('usa').category('demographics').datasets[0].variables[0]
            >>> filters = {variable.id: "= '2019-09-01'"}
            >>> gdf_enrich = Enrichment().enrich_polygons(
            ...     df,
            ...     variables=[variable],
            ...     filters=filters,
            ...     geom_col='the_geom')

            Enrich a polygons dataframe overwriting every variables aggregation method to use `SUM` function:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:3]
            >>> gdf_enrich = Enrichment().enrich_polygons(
            ...     df,
            ...     variables,
            ...     aggregation='SUM',
            ...     geom_col='the_geom')

            Enrich a polygons dataframe overwriting some of the variables aggregation methods:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM'
            >>> variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
            >>> variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'
            >>> variables = [variable1, variable2, variable3]
            >>> aggregation = {
            ...     variable1.id: 'SUM',
            ...     variable3.id: 'AVG'
            >>> }
            >>> gdf_enrich = Enrichment().enrich_polygons(
            ...     df,
            ...     variables,
            ...     aggregation=aggregation,
            ...     geom_col='the_geom')

            Enrich a polygons dataframe using several aggregation methods for a variable:

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variable1 = all_variables[0] // variable1.agg_method is 'AVG' but you want 'SUM' and 'AVG'
            >>> variable2 = all_variables[1] // variable2.agg_method is 'AVG' and it is what you want
            >>> variable3 = all_variables[2] // variable3.agg_method is 'SUM' but you want 'AVG'
            >>> variables = [variable1, variable2, variable3]
            >>> aggregation = {
            ...     variable1.id: ['SUM', 'AVG'],
            ...     variable3.id: 'AVG'
            >>> }
            >>> cdf_enrich = Enrichment().enrich_polygons(df, variables, aggregation=aggregation)

            Enrich a polygons dataframe without aggregating variables (because you want to it yourself, for example,
                in case you want to use your custom function for aggregating the data):

            >>> df = pandas.read_csv('path/to/local/csv')
            >>> all_variables = Catalog().country('usa').category('demographics').datasets[0].variables
            >>> variables = all_variables[:3]
            >>> gdf_enrich = Enrichment().enrich_polygons(
            ...     df,
            ...     variables,
            ...     aggregation=None,
            ...     geom_col='the_geom')

            The next example uses filters to calculate the `SUM` of car-free households
            :obj:`Variable` of the :obj:`Catalog` for each polygon of `my_local_dataframe` pandas `DataFrame` only for
            areas with more than 100 car-free households:

            >>> variable = Variable.get('no_cars_d19dfd10')
            >>> gdf_enrich = Enrichment().enrich_polygons(
            ...     my_local_dataframe,
            ...     variables=[variable],
            ...     aggregation={variable.id: 'SUM'},
            ...     filters={variable.id: '> 100'},
            ...     geom_col='the_geom')

        """
        return self._enrich(GEOM_TYPE_POLYGONS, dataframe, variables, geom_col, filters, aggregation)

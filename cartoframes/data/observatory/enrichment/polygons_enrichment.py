from __future__ import absolute_import

from .enrichment_service import enrich


def enrich_polygons(data, variables, agg_operators=dict(), data_geom_column='geometry',
                    filters=dict(), credentials=None):
    """enrich_polygons

    Enrich a polygons dataset

    This method allows you to enrich your dataset with columns from our data, intersecting
    your polygons with our geographies. When a polygon intersects with multiple geographies of our
    dataset, the proportional part of the intersection will be used to interpolate the quantity of the
    polygon value intersected, aggregating them with the operator provided by `agg_operators` argument.

    Args:
        data (Dataset, DataFrame, GeoDataFrame): a Dataset, DataFrame or GeoDataFrame object to be enriched.
        variables (Variable, CatalogList, list, str): variable(s), discovered through Catalog,
            for enriching the `data` argument.
        agg_operators (dict, str, None, optional): dictionary with either a `column` key
            with the name of the column to aggregate or a `operator` value with the operator to group by.
            If `agg_operators`' dictionary is empty (default argument value) then aggregation operators
            will be retrieved from metadata column.
            If `agg_operators` is a string then all columns will be aggregated by this operator.
            If `agg_operators` is `None` then no aggregations will be computed. All the values which
            data geometry intersects with will be returned.
        data_geom_column (str): string indicating the 4326 geometry column in `data`.
        filters (dict, optional): dictionary with either a `column` key
            with the name of the column to filter or a `value` value with the value to filter by.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            credentials of user account. If not provided,
            a default credentials (if set with :py:meth:`set_default_credentials
            <cartoframes.auth.set_default_credentials>`) will attempted to be
            used.

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

    data_enriched = enrich(_prepare_sql, data=data, variables=variables, agg_operators=agg_operators,
                           data_geom_column=data_geom_column, filters=filters, credentials=credentials)

    return data_enriched


def _prepare_sql(enrichment_id, filters_processed, table_to_geotable, table_to_variables,
                 table_to_project, table_to_dataset, user_dataset, working_project,
                 data_table, **kwargs):

    grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=enrichment_id)

    sqls = list()

    for table, variables in table_to_variables.items():
        agg_operators = kwargs.get('agg_operators')

        if agg_operators is not None:

            if isinstance(agg_operators, str):
                agg_operators = {variable: agg_operators for variable in variables}

            variables_sql = ['{operator}(enrichment_table.{variable} * \
                              (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                              / ST_area(data_table.{data_geom_column}))) as {variable}'.format(variable=variable,
                             data_geom_column=kwargs['data_geom_column'],
                            operator=agg_operators[variable]) for variable in variables]

        else:
            variables_sql = ['enrichment_table.{}'.format(variable) for variable in variables] +\
                 ['ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                    / ST_area(data_table.{data_geom_column}) AS measures_proportion'.format(
                        data_geom_column=kwargs['data_geom_column'])]

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
        '''.format(enrichment_id=enrichment_id, variables=', '.join(variables_sql),
                   enrichment_table=table, enrichment_geo_table=table_to_geotable[table],
                   user_dataset=user_dataset, working_project=working_project,
                   data_table=data_table, data_geom_column=kwargs['data_geom_column'],
                   filters=filters_processed, grouper=grouper, project=table_to_project[table],
                   dataset=table_to_dataset[table])

        sqls.append(sql)

    return sqls

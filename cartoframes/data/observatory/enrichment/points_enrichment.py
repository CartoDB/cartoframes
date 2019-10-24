from __future__ import absolute_import

from .enrichment_service import enrich


def enrich_points(data, variables, data_geom_column='geometry', filters=dict(), credentials=None):
    """enrich_points

    Enrich a points dataset

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

    data_enriched = enrich(_prepare_sql, data=data, variables=variables, data_geom_column=data_geom_column,
                           filters=filters, credentials=credentials)

    return data_enriched


def _prepare_sql(enrichment_id, filters_processed, table_to_geotable, table_to_variables,
                 table_to_project, table_to_dataset, user_dataset, working_project,
                 data_table, **kwargs):

    sqls = list()

    for table, variables in table_to_variables.items():

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
        '''.format(enrichment_id=enrichment_id, enrichment_table=table,
                   enrichment_geo_table=table_to_geotable[table], user_dataset=user_dataset,
                   working_project=working_project, data_table=data_table,
                   data_geom_column=kwargs['data_geom_column'], filters=filters_processed,
                   project=table_to_project[table], dataset=table_to_dataset[table],
                   variables=', '.join(['enrichment_table.{}'.format(variable) for variable in variables]))

        sqls.append(sql)

    return sqls

from __future__ import absolute_import

from .enrichment_service import enrich

# TODO: process column name in metadata, remove spaces and points


def enrich_points(data, variables, data_geom_column='geometry', filters=dict(), credentials=None):
    """enrich_points

    This method is responsible for # TODO

    Args:
        data: # TODO
        variables: # TODO
        data_geom_column: # TODO
        filters: # TODO
        credentials: # TODO
    """

    data_enriched = enrich(_prepare_sql, data=data, variables=variables, data_geom_column=data_geom_column,
                           filters=filters, credentials=credentials)

    return data_enriched


def _prepare_sql(enrichment_id, filters_processed, table_to_geotable, table_to_variables,
                 table_to_project, table_to_dataset, geotable_to_project, geotable_to_dataset,
                 user_dataset, working_project, data_table, **kwargs):

    sqls = list()

    for table, variables in table_to_variables.items():

        sql = '''
            SELECT data_table.{enrichment_id},
                {variables},
                ST_Area(enrichment_geo_table.geom) AS {variables_underscored}_area,
                NULL AS {variables_underscored}_population
            FROM `{project}.{dataset}.{enrichment_table}` enrichment_table
            JOIN `{geo_project}.{geo_dataset}.{enrichment_geo_table}` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `{working_project}.{user_dataset}.{data_table}` data_table
            ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            {filters};
        '''.format(enrichment_id=enrichment_id, variables=', '.join(variables),
                   variables_underscored='_'.join(variables), enrichment_table=table,
                   enrichment_geo_table=table_to_geotable[table], user_dataset=user_dataset,
                   working_project=working_project, data_table=data_table,
                   data_geom_column=kwargs['data_geom_column'], filters=filters_processed,
                   project=table_to_project[table], dataset=table_to_dataset[table],
                   geo_project=geotable_to_project[table], geo_dataset=geotable_to_dataset[table])

        sqls.append(sql)

    return sqls

from .enrichment_utils import enrich

# TODO: process column name in metadata, remove spaces and points


def enrich_points(data, variables, data_geom_column='geometry', filters=dict(), credentials=None):

    data_enriched = enrich(__prepare_sql, data=data, variables=variables, data_geom_column=data_geom_column,
                           filters=filters, credentials=credentials)

    return data_enriched


def __prepare_sql(enrichment_id, filters_processed, variables_processed, enrichment_table,
                  enrichment_geo_table, user_dataset, working_project, data_table, **kwargs):

    sql = '''
        SELECT data_table.{enrichment_id},
              {variables},
              ST_Area(enrichment_geo_table.geom) AS area,
              NULL AS population
        FROM `{working_project}.{user_dataset}.{enrichment_table}` enrichment_table
        JOIN `{working_project}.{user_dataset}.{enrichment_geo_table}` enrichment_geo_table
          ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{working_project}.{user_dataset}.{data_table}` data_table
          ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {filters};
    '''.format(enrichment_id=enrichment_id, variables=', '.join(variables_processed),
               enrichment_table=enrichment_table, enrichment_geo_table=enrichment_geo_table,
               user_dataset=user_dataset, working_project=working_project,
               data_table=data_table, data_geom_column=kwargs['data_geom_column'],
               filters=filters_processed)

    return sql

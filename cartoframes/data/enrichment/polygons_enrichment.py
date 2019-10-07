from __future__ import absolute_import

from .enrichment_service import enrich


# TODO: process column name in metadata, remove spaces and points


def enrich_polygons(data, variables, agg_operators, data_geom_column='geometry', filters=dict(), credentials=None):
    """enrich_polygons

    This method is responsible for # TODO

    Args:
        data: # TODO
        variables: # TODO
        agg_operators: # TODO
        data_geom_column: # TODO
        filters: # TODO
        credentials: # TODO
    """

    data_enriched = enrich(_prepare_sql, data=data, variables=variables, agg_operators=agg_operators,
                           data_geom_column=data_geom_column, filters=filters, credentials=credentials)

    return data_enriched


def _prepare_sql(enrichment_id, filters_processed, variables_processed, enrichment_table,
                 enrichment_geo_table, user_dataset, working_project, data_table, **kwargs):

    grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=enrichment_id)

    if 'agg_operators' in kwargs:

        if isinstance(kwargs['agg_operators'], str):
            agg_operators = {variable: kwargs['agg_operators'] for variable in variables_processed}
        else:
            agg_operators = kwargs['agg_operators']

        variables_sql = ['{operator}({variable} * \
                         (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                         / ST_area(data_table.{data_geom_column}))) as {variable}'.format(
                             variable=variable,
                             data_geom_column=kwargs['data_geom_column'],
                             operator=agg_operators[variable]) for variable in variables_processed]

    else:
        variables_sql = variables_processed + ['ST_Area(ST_Intersection(geo_table.geom, data_table.{data_geom_column}))\
                                               / ST_area(data_table.{data_geom_column}) AS measures_proportion'.format(
                                                   data_geom_column=kwargs['data_geom_column'])]
        grouper = ''

    sql = '''
        SELECT data_table.{enrichment_id}, {variables}
        FROM `{working_project}.{user_dataset}.{enrichment_table}` enrichment_table
        JOIN `{working_project}.{user_dataset}.{enrichment_geo_table}` enrichment_geo_table
          ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{working_project}.{user_dataset}.{data_table}` data_table
          ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {filters}
        {grouper};
    '''.format(enrichment_id=enrichment_id, variables=', '.join(variables_sql),
               enrichment_table=enrichment_table, enrichment_geo_table=enrichment_geo_table,
               user_dataset=user_dataset, working_project=working_project,
               data_table=data_table, data_geom_column=kwargs['data_geom_column'],
               filters=filters_processed, grouper=grouper)

    return sql

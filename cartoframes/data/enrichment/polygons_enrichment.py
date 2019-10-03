from .enrichment_service import enrich

# TODO: process column name in metadata, remove spaces and points


def enrich_polygons(data, variables, agg_operators, data_geom_column='geometry', filters=dict(), credentials=None):

    data_enriched = enrich(_prepare_sql, data=data, variables=variables, agg_operators=agg_operators,
                           data_geom_column=data_geom_column, filters=filters, credentials=credentials)

    return data_enriched


def _prepare_sql(enrichment_id, filters_processed, table_to_geotable, table_to_variables,
                 table_to_project, table_to_dataset, user_dataset, working_project, data_table, **kwargs):

    grouper = 'group by data_table.{enrichment_id}'.format(enrichment_id=enrichment_id)

    sqls = list()

    for table, variables in table_to_variables.items():

        if 'agg_operators' in kwargs:

            if isinstance(kwargs['agg_operators'], str):
                agg_operators = {variable: kwargs['agg_operators'] for variable in variables}
            else:
                agg_operators = kwargs['agg_operators']

            variables_sql = ['{operator}({variable} * \
                              (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                              / ST_area(data_table.{data_geom_column}))) as {variable}'.format(variable=variable,
                             data_geom_column=kwargs['data_geom_column'],
                            operator=agg_operators[variable]) for variable in variables]

        else:
            variables_sql = variables + ['ST_Area(ST_Intersection(geo_table.geom, data_table.{data_geom_column}))\
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

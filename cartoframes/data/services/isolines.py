from __future__ import absolute_import

from ...data import Dataset
from .service import Service
import pandas as pd


QUOTA_SERVICE = 'isolines'


class Isolines(Service):

    def __init__(self, credentials=None):
        super(Isolines, self).__init__(credentials, quota_service=QUOTA_SERVICE)

    def isochrone_areas(self, source, range, **args):
        return self._iso_areas(source, range, function='isochrone', **args)

    def isodistance_areas(self, source, range, **args):
        return self._iso_areas(source, range, function='isodistance', **args)

    def _iso_areas(self,
                   source,
                   range,
                   dry_run=False,
                   table_name=None,
                   if_exists=None,
                   is_destination=None,
                   mode='car',
                   mode_type=None,
                   mode_traffic=None,
                   resolution=None,
                   maxpoints=None,
                   quality=None,
                   with_source_id=True,
                   with_source_geom=False,
                   rings=False,
                   function=None):
        # we could default source_id=True for table source and
        # source_geom=True for dataframe source

        metadata = {}

        input_dataframe = None
        if isinstance(source, pd.DataFrame):
            input_dataframe = source
            source = Dataset(input_dataframe, credentials=self._credentials)

        if dry_run:
            num_rows = source.get_num_rows()
            metadata['required_quota'] = num_rows * len(range)
            return self.result(data=None, metadata=metadata)

        source_columns = source.get_column_names()

        temporary_table_name = False

        if source.table_name:
            source_query = 'SELECT * FROM {table}'.format(table=source.table_name)
        elif source.get_query():
            source_query = source.get_query()
        else:  # source.is_local()
            # upload to temporary table
            temporary_table_name = self._new_temporary_table_name()
            source.upload(table_name=temporary_table_name, credentials=self._credentials)
            source_query = 'SELECT * FROM {table}'.format(table=temporary_table_name)

        iso_function = '_cdb_{function}_exception_safe'.format(function=function)
        # TODO: use **options argument?
        options = {
            'is_destination': is_destination,
            'mode_type': mode_type,
            'mode_traffic': mode_traffic,
            'resolution': resolution,
            'maxpoints': maxpoints,
            'quality': quality
        }
        iso_options = [str(k)+'='+str(v) for k, v in options.items() if v is not None]
        iso_options = "ARRAY[{opts}]".format(opts=','.join(iso_options))
        iso_ranges = 'ARRAY[{ranges}]'.format(ranges=','.join([str(r) for r in range]))

        if with_source_geom:
            # the source_geom is available as the `center` column in the iso_function result,
            # but this is not supported ATM, because we have not control over wich geometry
            # column is picked as `the_geom` in the cartodbfied table`
            raise ValueError('The with_source_geom option is not supported')

        sql = _areas_query(
            source_query, source_columns, iso_function, mode, iso_ranges, iso_options, with_source_id or rings)
        if rings:
            sql = _rings_query(sql, with_source_id)

        dataset = Dataset(sql, credentials=self._credentials)
        if table_name:
            dataset.upload(table_name=table_name, credentials=self._credentials, if_exists=if_exists)
            result = Dataset(table_name, credentials=self._credentials)
            if input_dataframe is not None:
                result = result.download()
        else:
            # It would be nice to use execute_long_running_query, but we need the results
            result = dataset.download()
            if input_dataframe is None:
                result = Dataset(result, credentials=self._credentials)

        if temporary_table_name:
            Dataset(temporary_table_name, credentials=self._credentials).delete()

        return self.result(result)


def _areas_query(source_query, source_columns, iso_function, mode, iso_ranges, iso_options, with_source_id):
    select_source_id = 'source_id,' if with_source_id else ''
    source_id = ''
    if with_source_id:
        if 'cartodb_id' in source_columns:
            source_id = '_source.cartodb_id AS source_id,'
        else:
            source_id = 'row_number() over () AS source_id'

    return """
        WITH _source AS ({source_query}),
        _iso_areas AS (
            SELECT
              _source.cartodb_id AS source_id,
              _source.the_geom AS source_geom,
              {iso_function}(
                  _source.the_geom,
                  '{mode}',
                  {iso_ranges}::integer[],
                  {iso_options}::text[]
              ) AS _area
            FROM _source
        )
        SELECT
          row_number() OVER () AS cartodb_id,
          {select_source_id}
          (_area).data_range,
          (_area).the_geom
        FROM _iso_areas
    """.format(
            iso_function=iso_function,
            source_query=source_query,
            source_id=source_id,
            select_source_id=select_source_id,
            mode=mode,
            iso_ranges=iso_ranges,
            iso_options=iso_options
        )


def _rings_query(areas_query, with_source_id):
    if with_source_id:
        select_source_id = 'source_id,'
    else:
        select_source_id = ''

    return """
        SELECT
            cartodb_id,
            {select_source_id}
            data_range,
            COALESCE(
              LAG(data_range, 1) OVER (PARTITION BY source_id ORDER BY data_range),
              0
            ) AS lower_data_range,
            COALESCE(
              ST_DIFFERENCE(the_geom, LAG(the_geom, 1) OVER (PARTITION BY source_id ORDER BY data_range)),
              the_geom
            ) AS the_geom
        FROM ({areas_query}) _areas_query
    """.format(
        select_source_id=select_source_id,
        areas_query=areas_query
    )

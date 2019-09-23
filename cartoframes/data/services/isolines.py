from __future__ import absolute_import

from ...lib import context
from ...auth import get_default_credentials
from ...data import Dataset
from .service import Service
import pandas as pd
import uuid


QUOTA_SERVICE = 'isolines'


class Isolines(Service):

    def __init__(self, credentials=None):
        super(Isolines, self).__init__(credentials, quota_service=QUOTA_SERVICE)

    def isochrones(self, source, range, **args):
        return self._iso(source, range, function='isochrone', **args)

    def isodistances(self, source, range, **args):
        return self._iso(source, range, function='isodistance', **args)

    def _iso(self,
             source,
             range,
             dry_run=False,
             table_name=None,
             if_exists=None,
             dataframe=False,
             is_destination=None,
             mode='car',
             mode_type=None,
             mode_traffic=None,
             resolution=None,
             maxpoints=None,
             quality=None,
             with_source_id=True,
             with_source_geom=False,
             function=None):
        # we could default source_id=True for table source and
        # source_geom=True for dataframe source

        input_dataframe = None
        if isinstance(source, pd.DataFrame):
            input_dataframe = source
            source = Dataset(input_dataframe)

        if dry_run:
            num_rows = self._dataset_num_rows(source)
            return {'required_quota': num_rows * len(range)}

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
        source_geom = 'source_geom,' if with_source_geom else ''  # TODO: this is redundant with `center`
        source_id = 'source_id,' if with_source_id else ''
        iso_ranges = 'ARRAY[{ranges}]'.format(ranges=','.join([str(r) for r in range]))

        sql = """
          WITH _source AS ({source_query}),
          _isos AS (
              SELECT
                _source.cartodb_id AS source_id,
                _source.the_geom AS source_geom,
                {iso_function}(
                    _source.the_geom,
                    '{mode}',
                    {iso_ranges}::integer[],
                    {iso_options}::text[]
                ) AS _iso
              FROM _source
          )
          SELECT
            row_number() OVER () AS cartodb_id,
            {source_id}
            {source_geom}
            (_iso).data_range,
            (_iso).center,
            (_iso).the_geom
          FROM _isos
        """.format(
              iso_function=iso_function,
              source_query=source_query,
              source_id=source_id,
              source_geom=source_geom,
              mode=mode,
              iso_ranges=iso_ranges,
              iso_options=iso_options
            )

        if table_name:
            dataset = Dataset(sql, credentials=self._credentials)
            dataset.upload(table_name=table_name, credentials=self._credentials, if_exists=if_exists)
            result = Dataset(table_name, credentials=self.credential)
            # TODO: return a Dataframe if the input was a Dataframe
            # if input_dataframe:
            #     result = result.download()
        else:
            # It would be nice to use execute_long_running_query, but we need the results
            result = Dataset(sql, credentials=self._credentials).download()
            # TODO: should we return a Dataset if the input was not a Dataframe?
            # if not input_dataframe:
            #     result = Dataset(result)

        if temporary_table_name:
            Dataset(temporary_table_name, credentials=self._credentials).delete()

        return result

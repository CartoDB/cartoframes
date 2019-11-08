from __future__ import absolute_import

import pandas as pd

from ...utils.geom_utils import geodataframe_from_dataframe
from ...data import Dataset
from .service import Service

QUOTA_SERVICE = 'isolines'


class Isolines(Service):
    """Time and distance Isoline services using CARTO dataservices.
    """

    def __init__(self, credentials=None):
        super(Isolines, self).__init__(credentials, quota_service=QUOTA_SERVICE)

    def isochrones(self, source, ranges, **args):
        """isochrone areas

        This method computes areas delimited by isochrone lines (lines of constant travel time) based upon public roads.

        Args:
            source (Dataset, Dataframe): containing the source points for the isochrones:
                travel routes from the source points are computed to determine areas within
                specified travel times.
            ranges (list): travel time values in seconds; for each range value and source point a result polygon
                will be produced enclosing the area within range of the source.
            exclusive (bool, optional): when False (the default), inclusive range areas are generated, each one
                containing the areas for smaller time values (so the area is reachable from the source
                whithin the given time). When True, areas are exclusive, each one corresponding time values
                between the immediately smaller range value (or zero) and the area range value,
            table_name (str, optional): the resulting areas will be saved in a new
                CARTO table with this name.
            if_exists (str, optional): Behavior for creating new datasets, only applicable
                if table_name isn't None;
                Options are 'fail', 'replace', or 'append'. Defaults to 'fail'.
            dry_run (bool, optional): no actual computattion will be performed,
                and metadata will be returned including the required quota.
            mode (str, optional):  defines the travel mode: ``'car'`` (the default) or ``'walk'``.
            is_destination (bool, optional):  indicates that the source points are to be taken as
                destinations for the routes used to compute the area, rather than origins.
            mode_type (str, optional): type of routes computed: ``'shortest'`` (default) or ``'fastests'``.
            mode_traffic (str, optional): use traffic data to compute routes: ``'disabled'`` (default) or ``'enabled'``.
            resolution (float, optional): level of detail of the polygons in meters per pixel.
                Higher resolution may increase the response time of the service.
            maxpoints (int, optional): Allows to limit the amount of points in the returned polygons.
                Increasing the number of maxpoints may increase the response time of the service.
            quality: (int, optional): Allows you to reduce the quality of the polygons in favor of the response time.
                Admitted values: 1/2/3.
            with_lnglat (tuple, optional): Two columns that have the longitude
                and latitude information. If used, a point geometry will be
                created upon upload to CARTO. Example input: `('long', 'lat')`.
                Defaults to `None`.

        Returns:
            A named-tuple ``(data, metadata)`` containing  either a ``data`` Dataset or DataFrame
            (same type as the input ``source``) and a ``metadata`` dictionary.
            For dry runs the data will be ``None``.
            The data contains a ``range_data`` column with a numeric value and a ``the_geom``
            geometry with the corresponding area. It will also contain a ``source_id`` column
            that identifies the source point corresponding to each area if the source has a
            ``cartodb_id`` column.
        """
        return self._iso_areas(source, ranges, function='isochrone', **args)

    def isodistances(self, source, ranges, **args):
        """isodistance areas

        This method computes areas delimited by isodistance lines (lines of constant travel distance) based upon public
        roads.

        Args:
            source (Dataset, Dataframe): containing the source points for the isochrones:
                travel routes from the source points are computed to determine areas within
                specified travel distances.
            ranges (list): travel distance values in meters; for each range value and source point a result polygon
                will be produced enclosing the area within range of the source.
            exclusive (bool, optional): when False (the default), inclusive range areas are generated, each one
                containing the areas for smaller distance values (so the area is reachable from the source
                whithin the given distance). When True, areas are exclusive, each one corresponding distance values
                between the immediately smaller range value (or zero) and the area range value,
            table_name (str, optional): the resulting areas will be saved in a new
                CARTO table with this name.
            if_exists (str, optional): Behavior for creating new datasets, only applicable
                if table_name isn't None;
                Options are 'fail', 'replace', or 'append'. Defaults to 'fail'.
            dry_run (bool, optional): no actual computattion will be performed,
                and metadata will be returned including the required quota.
            mode (str, optional):  defines the travel mode: ``'car'`` (the default) or ``'walk'``.
            is_destination (bool, optional):  indicates that the source points are to be taken as
                destinations for the routes used to compute the area, rather than origins.
            mode_type (str, optional): type of routes computed: ``'shortest'`` (default) or ``'fastests'``.
            mode_traffic (str, optional): use traffic data to compute routes: ``'disabled'`` (default) or ``'enabled'``.
            resolution (float, optional): level of detail of the polygons in meters per pixel.
                Higher resolution may increase the response time of the service.
            maxpoints (int, optional): Allows to limit the amount of points in the returned polygons.
                Increasing the number of maxpoints may increase the response time of the service.
            quality: (int, optional): Allows you to reduce the quality of the polygons in favor of the response time.
                Admitted values: 1/2/3.
            with_lnglat (tuple, optional): Two columns that have the longitude
                and latitude information. If used, a point geometry will be
                created upon upload to CARTO. Example input: `('long', 'lat')`.
                Defaults to `None`.

        Returns:
            A named-tuple ``(data, metadata)`` containing  either a ``data`` Dataset or DataFrame
            (same type as the input ``source``) and a ``metadata`` dictionary.
            For dry runs the data will be ``None``.
            The data contains a ``range_data`` column with a numeric value and a ``the_geom``
            geometry with the corresponding area. It will also contain a ``source_id`` column
            that identifies the source point corresponding to each area if the source has a
            ``cartodb_id`` column.
        """
        return self._iso_areas(source, ranges, function='isodistance', **args)

    def _iso_areas(self,
                   source,
                   ranges,
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
                   exclusive=False,
                   with_lnglat=None,
                   function=None):
        metadata = {}

        input_dataframe = None
        if isinstance(source, pd.DataFrame):
            input_dataframe = source
            source = Dataset(input_dataframe)

        num_rows = source.get_num_rows()
        metadata['required_quota'] = num_rows * len(ranges)

        if dry_run:
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
            source.upload(table_name=temporary_table_name, credentials=self._credentials, with_lnglat=with_lnglat)
            source_query = 'SELECT * FROM {table}'.format(table=temporary_table_name)
            source_columns = source.get_column_names()

        source_has_id = 'cartodb_id' in source_columns

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
        iso_options = ["'{}={}'".format(k, v) for k, v in options.items() if v is not None]
        iso_options = "ARRAY[{opts}]".format(opts=','.join(iso_options))
        iso_ranges = 'ARRAY[{ranges}]'.format(ranges=','.join([str(r) for r in ranges]))

        sql = _areas_query(
            source_query, source_columns, iso_function, mode, iso_ranges, iso_options, source_has_id or exclusive)
        if exclusive:
            sql = _rings_query(sql, source_has_id)

        dataset = Dataset(sql, credentials=self._credentials)
        if table_name:
            dataset.upload(table_name=table_name, if_exists=if_exists)
            result = Dataset(table_name, credentials=self._credentials)
            if input_dataframe is not None:
                result = geodataframe_from_dataframe(result.download())
        else:
            result = geodataframe_from_dataframe(dataset.download())
            if input_dataframe is None:
                result = Dataset(result, credentials=self._credentials)

        if temporary_table_name:
            Dataset(temporary_table_name, credentials=self._credentials).delete()

        return self.result(data=result, metadata=metadata)


def _areas_query(source_query, source_columns, iso_function, mode, iso_ranges, iso_options, with_source_id):
    select_source_id = 'source_id,' if with_source_id else ''
    source_id = ''
    if with_source_id:
        if 'cartodb_id' in source_columns:
            source_id = '_source.cartodb_id AS source_id,'
        else:
            source_id = 'row_number() over () AS source_id,'

    return """
        WITH _source AS ({source_query}),
        _iso_areas AS (
            SELECT
              {source_id}
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

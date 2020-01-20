# -*- coding: utf-8 -*-

import json
import collections

from warnings import warn
from pandas import DataFrame
from carto.exceptions import CartoException

from ...io.carto import read_carto, to_carto
from ...utils import utils
from ...io.managers.context_manager import ContextManager


class DataObsClient:
    """Data Observatory v1 class. `Data Observatory documentation
    <https://carto.com/developers/data-observatory/>`__.

    This class provides the following methods to interact with Data Observatory:
        - boundaries: returns a geopandas.GeoDataFrame with
            the geographic boundaries (geometries) or their metadata.
        - discovery: returns a pandas.DataFrame with the measures found.
        - augment: returns a geopandas.GeoDataFrame with the augmented data.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`):
            A :py:class:`Credentials <cartoframes.auth.Credentials>`
            instance can be used in place of a `username`|`base_url` / `api_key` combination.
    """

    def __init__(self, credentials=None):
        self._verbose = 0
        self._credentials = credentials
        self._manager = ContextManager(credentials)

    def boundaries(self, boundary=None, region=None, decode_geom=False,
                   timespan=None, include_nonclipped=False):
        """
        Find all boundaries available for the world or a `region`. If
        `boundary` is specified, get all available boundary polygons for the
        region specified (if any). This method is especially useful for getting
        boundaries for a region and, with :py:meth:`DataObsClient.augment
        <cartoframes.client.DataObsClient.augment>` and
        :py:meth:`DataObsClient.discovery
        <cartoframes.client.DataObsClient.discovery>`, getting tables of
        geometries and the corresponding raw measures. For example, if you want
        to analyze how median income has changed in a region (see examples
        section for more).

        Examples:
            Find all boundaries available for Australia. The columns
            `geom_name` gives us the name of the boundary and `geom_id`
            is what we need for the `boundary` argument.

            >>> do = DataObsClient(credentials)
            >>> au_boundaries = do.boundaries(region='Australia')
            >>> au_boundaries[['geom_name', 'geom_id']]

            Get the boundaries for Australian Postal Areas and map them.

            >>> au_postal_areas = do.boundaries(boundary='au.geo.POA')
            >>> Map(Layer(au_postal_areas))

            Get census tracts around Idaho Falls, Idaho, USA, and add median
            income from the US census. Without limiting the metadata, we get
            median income measures for each census in the Data Observatory.

            >>> # Note: default credentials will be supported in a future release
            >>> do = DataObsClient(credentials)
            >>> # will return GeoDataFrame with columns `the_geom` and `geom_ref`
            >>> tracts = do.boundaries(
            ...     boundary='us.census.tiger.census_tract',
            ...     region=[-112.096642,43.429932,-111.974213,43.553539])
            >>> # write geometries to a CARTO table
            >>> tracts.upload('idaho_falls_tracts')
            >>> # gather metadata needed to look up median income
            >>> median_income_meta = do.discovery(
            ...     'idaho_falls_tracts',
            ...     keywords='median income',
            ...     boundaries='us.census.tiger.census_tract')
            >>> # get median income data and original table as new GeoDataFrame
            >>> idaho_falls_income = do.augment(
            ...     'idaho_falls_tracts',
            ...     median_income_meta,
            ...     how='geom_refs')
            >>> # overwrite existing table with newly-enriched GeoDataFrame
            >>> idaho_falls_income.upload('idaho_falls_tracts', if_exists='replace')

        Args:
            boundary (str, optional):
                Boundary identifier for the boundaries
                that are of interest. For example, US census tracts have a
                boundary ID of ``us.census.tiger.census_tract``, and Brazilian
                Municipios have an ID of ``br.geo.municipios``. Find IDs by
                running :py:meth:`DataObsClient.boundaries
                <cartoframes.client.DataObsClient.boundaries>`
                without any arguments, or by looking in the `Data Observatory
                catalog <http://cartodb.github.io/bigmetadata/>`__.
            region (str, optional):
                Region where boundary information or,
                if `boundary` is specified, boundary polygons are of interest.
                `region` can be one of the following:

                    - table name (str):
                        Name of a table in user's CARTO account
                    - bounding box (list of float):
                        List of four values (two lng/lat pairs) in the following order:
                        western longitude, southern latitude, eastern longitude,
                        and northern latitude.
                        For example, Switzerland fits in
                        ``[5.9559111595,45.8179931641,10.4920501709,47.808380127]``
            timespan (str, optional):
                Specific timespan to get geometries from.
                Defaults to use the most recent. See the Data Observatory catalog
                for more information.
            decode_geom (bool, optional):
                Whether to return the geometries as
                Shapely objects or keep them encoded as EWKB strings. Defaults
                to False.
            include_nonclipped (bool, optional):
                Optionally include non-shoreline-clipped boundaries.
                These boundaries are the raw boundaries provided by, for example,
                US Census Tiger.

        Returns:
            geopandas.GeoDataFrame:
                If `boundary` is specified, then all available
                boundaries and accompanying `geom_refs` in `region` (or the world
                if `region` is ``None`` or not specified) are returned. If
                `boundary` is not specified, then a GeoDataFrame of all available
                boundaries in `region` (or the world if `region` is ``None``).
        """
        # TODO: create a function out of this?
        if isinstance(region, str):
            # see if it's a table
            try:
                geom_type = self._geom_type(region)
                if geom_type in ('point', 'line', ):
                    bounds = ('(SELECT ST_ConvexHull(ST_Collect(the_geom)) '
                              'FROM {table})').format(table=region)
                else:
                    bounds = ('(SELECT ST_Union(the_geom) '
                              'FROM {table})').format(table=region)
            except CartoException:
                # see if it's a Data Obs region tag
                regionsearch = '"geom_tags"::text ilike \'%{}%\''.format(
                    get_countrytag(region))
                bounds = 'ST_MakeEnvelope(-180.0, -85.0, 180.0, 85.0, 4326)'
        elif isinstance(region, collections.Iterable):
            if len(region) != 4:
                raise ValueError(
                    '`region` should be a list of the geographic bounds of a '
                    'region in the following order: western longitude, '
                    'southern latitude, eastern longitude, and northern '
                    'latitude. For example, Switerland fits in '
                    '``[5.9559111595,45.8179931641,10.4920501709,'
                    '47.808380127]``.')
            bounds = ('ST_MakeEnvelope({0}, {1}, {2}, {3}, 4326)').format(
                *region)
        elif region is None:
            bounds = 'ST_MakeEnvelope(-180.0, -85.0, 180.0, 85.0, 4326)'
        else:
            raise ValueError('`region` must be a str, a list of two lng/lat '
                             'pairs, or ``None`` (which defaults to the '
                             'world)')
        if include_nonclipped:
            clipped = None
        else:
            clipped = (r"(geom_id ~ '^us\.census\..*_clipped$' OR "
                       r"geom_id !~ '^us\.census\..*')")

        if boundary is None:
            regionsearch = locals().get('regionsearch')
            filters = ' AND '.join(r for r in [regionsearch, clipped] if r)
            query = utils.minify_sql((
                'SELECT *',
                'FROM OBS_GetAvailableGeometries(',
                '  {bounds}, null, null, null, {timespan})',
                '{filters}')).format(
                    bounds=bounds,
                    timespan=utils.pgquote(timespan),
                    filters='WHERE {}'.format(filters) if filters else '')
            return self._fetch(query, decode_geom=True)

        query = utils.minify_sql((
            'SELECT the_geom, geom_refs',
            'FROM OBS_GetBoundariesByGeometry(',
            '    {bounds},',
            '    {boundary},',
            '    {time})', )).format(
                bounds=bounds,
                boundary=utils.pgquote(boundary),
                time=utils.pgquote(timespan))
        return self._fetch(query, decode_geom=decode_geom)

    def discovery(self, region, keywords=None, regex=None, time=None,
                  boundaries=None, include_quantiles=False):
        """Discover Data Observatory measures. This method returns the full
        Data Observatory metadata model for each measure or measures that
        match the conditions from the inputs. The full metadata in each row
        uniquely defines a measure based on the timespan, geographic
        resolution, and normalization (if any). Read more about the metadata
        response in `Data Observatory
        <https://carto.com/developers/data-observatory/reference/#discovery-functions>`__
        documentation.

        Internally, this method finds all measures in `region` that match the
        conditions set in `keywords`, `regex`, `time`, and `boundaries` (if
        any of them are specified). Then, if `boundaries` is not specified, a
        geographical resolution for that measure will be chosen subject to the
        type of region specified:

          1. If `region` is a table name, then a geographical resolution that
             is roughly equal to `region size / number of subunits`.
          2. If `region` is a country name or bounding box, then a geographical
             resolution will be chosen roughly equal to `region size / 500`.

        Since different measures are in some geographic resolutions and not
        others, different geographical resolutions for different measures are
        oftentimes returned.

        .. tip::

            To remove the guesswork in how geographical resolutions are
            selected, specify one or more boundaries in `boundaries`. See
            the boundaries section for each region in the `Data Observatory
            catalog <http://cartodb.github.io/bigmetadata/>`__.

        The metadata returned from this method can then be used to create raw
        tables or for augmenting an existing table from these measures using
        :py:meth:`DataObsClient.augment <cartoframes.client.DataObsClient.augment>`.
        For the full Data Observatory catalog, visit
        https://cartodb.github.io/bigmetadata/. When working with the metadata
        DataFrame returned from this method, be careful to only remove rows not
        columns as `DataObsClient.augment <cartoframes.client.DataObsClient.augment>`
        generally needs the full metadata.

        .. note::
            Narrowing down a discovery query using the `keywords`, `regex`, and
            `time` filters is important for getting a manageable metadata
            set. Besides there being a large number of measures in the DO, a
            metadata response has acceptable combinations of measures with
            demonimators (normalization and density), and the same measure from
            other years.

            For example, setting the region to be United States counties with
            no filter values set will result in many thousands of measures.

        Examples:
            Get all European Union measures that mention ``freight``.

            >>> freight_meta = do.discovery('European Union',
            ...                        keywords='freight',
            ...                        time='2010')
            >>> freight_meta['numer_name'].head()

        Args:
            region (str or list of float):
                Information about the region of interest.
                `region` can be one of three types:

                    - region name (str):
                        Name of region of interest. Acceptable
                        values are limited to: 'Australia', 'Brazil', 'Canada',
                        'European Union', 'France', 'Mexico', 'Spain',
                        'United Kingdom', 'United States'.
                    - table name (str):
                        Name of a table in user's CARTO account
                        with geometries. The region will be the bounding box of
                        the table.

                  .. Note:: If a table name is also a valid Data Observatory
                      region name, the Data Observatory name will be chosen
                      over the table.

                - bounding box (list of float):
                    List of four values (two lng/lat pairs) in the following
                    order: western longitude, southern latitude, eastern longitude,
                    and northern latitude. For example, Switzerland fits in
                    ``[5.9559111595,45.8179931641,10.4920501709,47.808380127]``

                .. Note:: Geometry levels are generally chosen by subdividing
                    the region into the next smallest administrative unit. To
                    override this behavior, specify the `boundaries` flag. For
                    example, set `boundaries` to
                    ``'us.census.tiger.census_tract'`` to choose US census
                    tracts.

            keywords (str or list of str, optional):
                Keyword or list of keywords in measure description or name.
                Response will be matched on all keywords listed (boolean `or`).

            regex (str, optional):
                A regular expression to search the measure
                descriptions and names. Note that this relies on PostgreSQL's
                case insensitive operator ``~*``. See `PostgreSQL docs
                <https://www.postgresql.org/docs/9.5/static/functions-matching.html>`__
                for more information.
            boundaries (str or list of str, optional):
                Boundary or list of boundaries that specify the measure resolution. See the
                boundaries section for each region in the `Data Observatory
                catalog <http://cartodb.github.io/bigmetadata/>`__.
            include_quantiles (bool, optional):
                Include quantiles calculations which are a calculation
                of how a measure compares to all measures in the full GeoDataFrame.
                Defaults to ``False``. If ``True``, quantiles columns will be returned
                for each column which has it pre-calculated.

        Returns:
            pandas.DataFrame:
                A DataFrame of the complete metadata model for specific measures based
                on the search parameters.

        Raises:
            ValueError: If `region` is a :obj:`list` and does not consist of
              four elements, or if `region` is not an acceptable region
            CartoException: If `region` is not a table in user account
        """
        if isinstance(region, str):
            try:
                # see if it's a DO region, nest in {}
                countrytag = '\'{{{0}}}\''.format(
                    get_countrytag(region))
                boundary = ('SELECT ST_MakeEnvelope(-180.0, -85.0, 180.0, '
                            '85.0, 4326) AS env, 500::int AS cnt')
            except ValueError:
                # TODO: make this work for general queries
                # see if it's a table
                self._manager.execute_query(
                    'EXPLAIN SELECT * FROM {}'.format(region))
                boundary = (
                    'SELECT ST_SetSRID(ST_Extent(the_geom), 4326) AS env, '
                    'count(*)::int AS cnt FROM {table_name}').format(
                        table_name=region)
        elif isinstance(region, collections.Iterable):
            if len(region) != 4:
                raise ValueError(
                    '`region` should be a list of the geographic bounds of a '
                    'region in the following order: western longitude, '
                    'southern latitude, eastern longitude, and northern '
                    'latitude. For example, Switerland fits in '
                    '``[5.9559111595,45.8179931641,10.4920501709,'
                    '47.808380127]``.'
                )
            boundary = ('SELECT ST_MakeEnvelope({0}, {1}, {2}, {3}, 4326) AS '
                        'env, 500::int AS cnt'.format(*region))

        if locals().get('countrytag') is None:
            countrytag = 'null'

        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords, ]
            kwsearch = ' OR '.join(
                ('numer_description ILIKE \'%{kw}%\' OR '
                 'numer_name ILIKE \'%{kw}%\'').format(kw=kw)
                for kw in keywords)
            kwsearch = '({})'.format(kwsearch)

        if regex:
            regexsearch = ('(numer_description ~* {regex} OR numer_name '
                           '~* {regex})').format(regex=utils.pgquote(regex))

        if keywords or regex:
            subjectfilters = '{kw} {op} {regex}'.format(
                kw=kwsearch if keywords else '',
                op='OR' if (keywords and regex) else '',
                regex=regexsearch if regex else '').strip()
        else:
            subjectfilters = ''

        if isinstance(time, str) or time is None:
            time = [time, ]
        if isinstance(boundaries, str) or boundaries is None:
            boundaries = [boundaries, ]

        if all(time) and all(boundaries):
            bt_filters = 'valid_geom AND valid_timespan'
        elif all(time) or all(boundaries):
            bt_filters = 'valid_geom' if all(boundaries) else 'valid_timespan'
        else:
            bt_filters = ''

        if bt_filters and subjectfilters:
            filters = 'WHERE ({s}) AND ({bt})'.format(
                s=subjectfilters, bt=bt_filters)
        elif bt_filters or subjectfilters:
            filters = 'WHERE {f}'.format(f=subjectfilters or bt_filters)
        else:
            filters = ''

        quantiles = ('WHERE numer_aggregate <> \'quantile\''
                     if not include_quantiles else '')

        numer_query = utils.minify_sql((
            'SELECT',
            '    numer_id,',
            '    {geom_id} AS geom_id,',
            '    {timespan} AS numer_timespan,',
            '    {normalization} AS normalization',
            '  FROM',
            '    OBS_GetAvailableNumerators(',
            '        (SELECT env FROM envelope),',
            '        {countrytag},',
            '        null,',  # denom_id
            '        {geom_id},',
            '        {timespan})',
            '{filters}', )).strip()

        # query all numerators for all `time`, `boundaries`, and raw/derived
        numers = '\nUNION\n'.join(
            numer_query.format(
                timespan=utils.pgquote(t),
                geom_id=utils.pgquote(b),
                normalization=utils.pgquote(n),
                countrytag=countrytag,
                filters=filters)
            for t in time
            for b in boundaries
            for n in ('predenominated', None))

        query = utils.minify_sql((
            'WITH envelope AS (',
            '    {boundary}',
            '), numers AS (',
            '  {numers}',
            ')',
            'SELECT *',
            'FROM json_to_recordset(',
            '    (SELECT OBS_GetMeta(',
            '        envelope.env,',
            '        json_agg(numers),',
            '        10, 10, envelope.cnt',
            '    ) AS meta',
            'FROM numers, envelope',
            'GROUP BY env, cnt)) as data(',
            '    denom_aggregate text, denom_colname text,',
            '    denom_description text, denom_geomref_colname text,',
            '    denom_id text, denom_name text, denom_reltype text,',
            '    denom_t_description text, denom_tablename text,',
            '    denom_type text, geom_colname text, geom_description text,',
            '    geom_geomref_colname text, geom_id text, geom_name text,',
            '    geom_t_description text, geom_tablename text,',
            '    geom_timespan text, geom_type text, id numeric,',
            '    max_score_rank text, max_timespan_rank text,',
            '    normalization text, num_geoms numeric, numer_aggregate text,',
            '    numer_colname text, numer_description text,',
            '    numer_geomref_colname text, numer_id text,',
            '    numer_name text, numer_t_description text,',
            '    numer_tablename text, numer_timespan text,',
            '    numer_type text, score numeric, score_rank numeric,',
            '    score_rownum numeric, suggested_name text,',
            '    target_area text, target_geoms text, timespan_rank numeric,',
            '    timespan_rownum numeric)',
            '{quantiles}', )).format(
                boundary=boundary,
                numers=numers,
                quantiles=quantiles).strip()
        utils.debug_print(self._verbose, query=query)
        return DataFrame(self._fetch(query, decode_geom=True))

    def augment(self, table_name, metadata, persist_as=None, how='the_geom'):
        """Get an augmented CARTO dataset with `Data Observatory
        <https://carto.com/data-observatory>`__ measures. Use
        `DataObsClient.discovery
        <#DataObsClient.discovery>`__ to search for available
        measures, or see the full `Data Observatory catalog
        <https://cartodb.github.io/bigmetadata/index.html>`__. Optionally
        persist the data as a new table.

        Example:
            Get a DataFrame with Data Observatory measures based on the
            geometries in a CARTO table.

            >>> do = DataObsClient(credentials)
            >>> median_income = do.discovery(
            ...     'transaction_events',
            ...     regex='.*median income.*',
            ...     time='2011 - 2015')
            >>> ds = do.augment('transaction_events', median_income)

            Pass in cherry-picked measures from the Data Observatory catalog.
            The rest of the metadata will be filled in, but it's important to
            specify the geographic level as this will not show up in the column
            name.

            >>> median_income = [{'numer_id': 'us.census.acs.B19013001',
            ...                   'geom_id': 'us.census.tiger.block_group',
            ...                   'numer_timespan': '2011 - 2015'}]
            >>> ds = do.augment('transaction_events', median_income)

        Args:
            table_name (str):
                Name of table on CARTO account that Data Observatory measures
                are to be added to.
            metadata (pandas.DataFrame):
                List of all measures to add to
                `table_name`. See :py:meth:`DataObsClient.discovery
                <cartoframes.client.DataObsClient.discovery>` outputs
                for a full list of metadata columns.
            persist_as (str, optional):
                Output the results of augmenting
                `table_name` to `persist_as` as a persistent table on CARTO.
                Defaults to ``None``, which will not create a table.
            how (str, optional):
                Column name for identifying the geometry from which to fetch the data.
                Defaults to `the_geom`, which results in measures that are spatially
                interpolated (e.g., a neighborhood boundary's population will
                be calculated from underlying census tracts). Specifying a
                column that has the geometry identifier (for example, GEOID for
                US Census boundaries), results in measures directly from the
                Census for that GEOID but normalized how it is specified in the
                metadata.

        Returns:
            geopandas.GeoDataFrame:
                A GeoDataFrame representation of `table_name` which
                has new columns for each measure in `metadata`.

        Raises:
            NameError:
                If the columns in `table_name` are in the ``suggested_name``
                column of `metadata`.
            ValueError:
                If metadata object is invalid or empty, or if the number of
                requested measures exceeds 50.
            CartoException:
                If user account consumes all of Data Observatory quota
        """

        if isinstance(metadata, DataFrame):
            _meta = metadata.copy().reset_index()
        elif isinstance(metadata, collections.Iterable):
            query = utils.minify_sql((
                'WITH envelope AS (',
                '  SELECT',
                '    ST_SetSRID(ST_Extent(the_geom)::geometry, 4326) AS env,',
                '    count(*)::int AS cnt',
                '  FROM {table_name}',
                ')',
                'SELECT *',
                '  FROM json_to_recordset(',
                '      (SELECT OBS_GetMeta(',
                '          envelope.env,',
                '          (\'{meta}\')::json,',
                '          10, 1, envelope.cnt',
                '      ) AS meta',
                '  FROM envelope',
                '  GROUP BY env, cnt)) as data(',
                '      denom_aggregate text, denom_colname text,',
                '      denom_description text, denom_geomref_colname text,',
                '      denom_id text, denom_name text, denom_reltype text,',
                '      denom_t_description text, denom_tablename text,',
                '      denom_type text, geom_colname text,',
                '      geom_description text,geom_geomref_colname text,',
                '      geom_id text, geom_name text, geom_t_description text,',
                '      geom_tablename text, geom_timespan text,',
                '      geom_type text, id numeric, max_score_rank text,',
                '      max_timespan_rank text, normalization text, num_geoms',
                '      numeric,numer_aggregate text, numer_colname text,',
                '      numer_description text, numer_geomref_colname text,',
                '      numer_id text, numer_name text, numer_t_description',
                '      text, numer_tablename text, numer_timespan text,',
                '      numer_type text, score numeric, score_rank numeric,',
                '      score_rownum numeric, suggested_name text,',
                '      target_area text, target_geoms text, timespan_rank',
                '      numeric, timespan_rownum numeric)',
            )).format(table_name=table_name,
                      meta=json.dumps(metadata).replace('\'', '\'\''))
            _meta = DataFrame(self._fetch(query))

        if _meta.shape[0] == 0:
            raise ValueError('There are no valid metadata entries. Check '
                             'inputs.')
        if _meta.shape[0] > 50:
            raise ValueError('The number of metadata entries exceeds 50. Tip: '
                             'If `metadata` is a pandas.DataFrame, iterate '
                             'over this object using `metadata.groupby`. If '
                             'it is a list, iterate over chunks of it. Then '
                             'combine resulting DataFrames using '
                             '`pandas.concat`')

        # get column names except the_geom_webmercator
        table_columns = self._manager.get_column_names(table_name, exclude=['the_geom_webmercator'])

        names = {}
        for suggested in _meta['suggested_name']:
            if suggested in table_columns:
                names[suggested] = utils.unique_colname(suggested, table_columns)
                warn(
                    '{s0} was augmented as {s1} because of name '
                    'collision'.format(s0=suggested, s1=names[suggested])
                )
            else:
                names[suggested] = suggested

        # drop description columns to lighten the query
        meta_columns = _meta.columns.values
        drop_columns = []
        for meta_column in meta_columns:
            if meta_column.endswith('_description'):
                drop_columns.append(meta_column)

        if len(drop_columns) > 0:
            _meta.drop(drop_columns, axis=1, inplace=True)

        cols = ', '.join(
            '(data->{n}->>\'value\')::{pgtype} AS {col}'.format(
                n=row[0],
                pgtype=row[1]['numer_type'],
                col=names[row[1]['suggested_name']])
            for row in _meta.iterrows())
        query = utils.minify_sql((
            'SELECT {table_cols}, {cols}',
            '  FROM OBS_GetData(',
            '       (SELECT array_agg({how})',
            '        FROM "{tablename}"),',
            '       (SELECT \'{meta}\'::json)) as m,',
            '       {tablename} as t',
            ' WHERE t."{rowid}" = m.id',)).format(
                how=('(the_geom, cartodb_id)::geomval'
                     if how == 'the_geom' else how),
                tablename=table_name,
                rowid='cartodb_id' if how == 'the_geom' else how,
                cols=cols,
                table_cols=','.join('t.{}'.format(c) for c in table_columns),
                meta=_meta.to_json(orient='records').replace('\'', '\'\''))

        return self._fetch(query, decode_geom=False, table_name=persist_as)

    def _fetch(self, query, decode_geom=False, table_name=None):
        gdf = read_carto(query, self._credentials, decode_geom=decode_geom)
        if table_name:
            to_carto(gdf, table_name, self._credentials,
                     geom_col='the_geom', if_exists='replace', log_enabled=False)
        return gdf

    def _geom_type(self, table):
        """gets geometry type(s) of specified layer"""
        query = 'SELECT * FROM "{table}"'.format(table=table)
        return self._manager.get_geom_type(query)


# Country names are pegged to the following query:
# SELECT
#    count(*) num_measurements,
#    tag.key region_id,
#    tag.value region_name
#  FROM (
#    SELECT *
#    FROM OBS_GetAvailableNumerators()
#    WHERE jsonb_pretty(numer_tags) LIKE '%subsection/%'
#  ) numers,
#  Jsonb_Each(numers.numer_tags) tag
#  WHERE tag.key like 'section%'
#  GROUP BY tag.key, tag.value
#  ORDER BY region_name


REGIONTAGS = {
    'Australia': 'section/tags.au',
    'Brazil': 'section/tags.br',
    'Canada': 'section/tags.ca',
    'European Union': 'section/tags.eu',
    'France': 'section/tags.fr',
    'Mexico': 'section/tags.mx',
    'Spain': 'section/tags.spain',
    'United Kingdom': 'section/tags.uk',
    'United States': 'section/tags.united_states'
}


def get_countrytag(country):
    """normalize country name to match data obs"""
    norm_name = {
        'australia': 'Australia',
        'brazil': 'Brazil',
        'brasil': 'Brazil',
        'canada': 'Canada',
        'european union': 'European Union',
        'eu': 'European Union',
        'e.u.': 'European Union',
        'france': 'France',
        'mexico': 'Mexico',
        'méxico': 'Mexico',
        'méjico': 'Mexico',
        'spain': 'Spain',
        'espana': 'Spain',
        'españa': 'Spain',
        'uk': 'United Kingdom',
        'u.k.': 'United Kingdom',
        'united kingdom': 'United Kingdom',
        'united states of america': 'United States',
        'united states': 'United States',
        'us': 'United States',
        'usa': 'United States',
        'u.s.': 'United States',
        'u.s.a.': 'United States'
    }
    if country is not None and country.lower() in norm_name:
        return REGIONTAGS.get(norm_name.get(country.lower()))
    else:
        raise ValueError(
            'The available regions are {0}.'.format(
                ', '.join('\'{}\''.format(k) for k in REGIONTAGS)))

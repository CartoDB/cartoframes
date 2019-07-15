from __future__ import absolute_import

from .. import context


class DataObs(object):
    """
    """

    def __init__(self, credentials, session=None):
        self._creds = credentials
        self._context = context.create_context(credentials, session)

    def boundaries(self):
        """Return a DataFrame with the geometries."""
        pass

    def discovery(self):
        """Return a metadata object with the result of the search."""
        pass
    
    def augment(self, dataset, metadata):
        """Augment the dataset with the provided metadata."""
        pass


    def data_boundaries(self, boundary=None, region=None, decode_geom=False,
                        timespan=None, include_nonclipped=False):
        """
        Find all boundaries available for the world or a `region`. If
        `boundary` is specified, get all available boundary polygons for the
        region specified (if any). This method is espeically useful for getting
        boundaries for a region and, with :py:meth:`Context.data
        <cartoframes.auth.Context.data>` and
        :py:meth:`Context.data_discovery
        <cartoframes.auth.Context.data_discovery>`, getting tables of
        geometries and the corresponding raw measures. For example, if you want
        to analyze how median income has changed in a region (see examples
        section for more).

        Examples:

            Find all boundaries available for Australia. The columns
            `geom_name` gives us the name of the boundary and `geom_id`
            is what we need for the `boundary` argument.

            .. code:: python

                import cartoframes
                con = cartoframes.auth.Context('base url', 'api key')
                au_boundaries = con.data_boundaries(region='Australia')
                au_boundaries[['geom_name', 'geom_id']]

            Get the boundaries for Australian Postal Areas and map them.

            .. code:: python

                from cartoframes import Layer
                au_postal_areas = con.data_boundaries(boundary='au.geo.POA')
                con.write(au_postal_areas, 'au_postal_areas')
                con.map(Layer('au_postal_areas'))

            Get census tracts around Idaho Falls, Idaho, USA, and add median
            income from the US census. Without limiting the metadata, we get
            median income measures for each census in the Data Observatory.

            .. code:: python

                con = cartoframes.auth.Context('base url', 'api key')
                # will return DataFrame with columns `the_geom` and `geom_ref`
                tracts = con.data_boundaries(
                    boundary='us.census.tiger.census_tract',
                    region=[-112.096642,43.429932,-111.974213,43.553539])
                # write geometries to a CARTO table
                con.write(tracts, 'idaho_falls_tracts')
                # gather metadata needed to look up median income
                median_income_meta = con.data_discovery(
                    'idaho_falls_tracts',
                    keywords='median income',
                    boundaries='us.census.tiger.census_tract')
                # get median income data and original table as new dataframe
                idaho_falls_income = con.data(
                    'idaho_falls_tracts',
                    median_income_meta,
                    how='geom_refs')
                # overwrite existing table with newly-enriched dataframe
                con.write(idaho_falls_income,
                         'idaho_falls_tracts',
                         overwrite=True)

        Args:
            boundary (str, optional): Boundary identifier for the boundaries
              that are of interest. For example, US census tracts have a
              boundary ID of ``us.census.tiger.census_tract``, and Brazilian
              Municipios have an ID of ``br.geo.municipios``. Find IDs by
              running :py:meth:`Context.data_boundaries
              <cartoframes.auth.Context.data_boundaries>`
              without any arguments, or by looking in the `Data Observatory
              catalog <http://cartodb.github.io/bigmetadata/>`__.
            region (str, optional): Region where boundary information or,
              if `boundary` is specified, boundary polygons are of interest.
              `region` can be one of the following:

                - table name (str): Name of a table in user's CARTO account
                - bounding box (list of float): List of four values (two
                  lng/lat pairs) in the following order: western longitude,
                  southern latitude, eastern longitude, and northern latitude.
                  For example, Switzerland fits in
                  ``[5.9559111595,45.8179931641,10.4920501709,47.808380127]``
            timespan (str, optional): Specific timespan to get geometries from.
              Defaults to use the most recent. See the Data Observatory catalog
              for more information.
            decode_geom (bool, optional): Whether to return the geometries as
              Shapely objects or keep them encoded as EWKB strings. Defaults
              to False.
            include_nonclipped (bool, optional): Optionally include
              non-shoreline-clipped boundaries. These boundaries are the raw
              boundaries provided by, for example, US Census Tiger.

        Returns:
            pandas.DataFrame: If `boundary` is specified, then all available
            boundaries and accompanying `geom_refs` in `region` (or the world
            if `region` is ``None`` or not specified) are returned. If
            `boundary` is not specified, then a DataFrame of all available
            boundaries in `region` (or the world if `region` is ``None``)
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
            return self.fetch(query, decode_geom=True)

        query = utils.minify_sql((
            'SELECT the_geom, geom_refs',
            'FROM OBS_GetBoundariesByGeometry(',
            '    {bounds},',
            '    {boundary},',
            '    {time})', )).format(
                bounds=bounds,
                boundary=utils.pgquote(boundary),
                time=utils.pgquote(timespan))
        return self.fetch(query, decode_geom=decode_geom)

    def fetch(self, query, decode_geom=False):
        """Pull the result from an arbitrary SELECT SQL query from a CARTO account
        into a pandas DataFrame.

        Args:
            query (str): SELECT query to run against CARTO user database. This data
              will then be converted into a pandas DataFrame.
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__.

        Returns:
            pandas.DataFrame: DataFrame representation of query supplied.
            Pandas data types are inferred from PostgreSQL data types.
            In the case of PostgreSQL date types, dates are attempted to be
            converted, but on failure a data type 'object' is used.

        Examples:
            This query gets the 10 highest values from a table and
            returns a dataframe.

            .. code:: python

                topten_df = con.query(
                    '''
                      SELECT * FROM
                      my_table
                      ORDER BY value_column DESC
                      LIMIT 10
                    '''
                )

            This query joins points to polygons based on intersection, and
            aggregates by summing the values of the points in each polygon. The
            query returns a dataframe, with a geometry column that contains
            polygons.

            .. code:: python

                points_aggregated_to_polygons = con.query(
                    '''
                      SELECT polygons.*, sum(points.values)
                      FROM polygons JOIN points
                      ON ST_Intersects(points.the_geom, polygons.the_geom)
                      GROUP BY polygons.the_geom, polygons.cartodb_id
                    ''',
                    decode_geom=True
                )

        """

        # self._context.download(query)
    
        dataset = Dataset.from_query(query, context=self)
        return dataset.download(decode_geom=decode_geom)

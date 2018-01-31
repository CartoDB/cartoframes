# -#- coding: utf-8 -#-
"""Analysis in cartoframes

Analysis in cartoframes takes two forms:

* :obj:`AnalysisChain` pipelines where multiple analyses can be chained off of
  a base node. This chain is lazily evaluated by applying a `.compute()` method
  after the chain is created. See :obj:`AnalysisChain` for more infomration.
* By chaining analysis methods off of a base node. See the methods of
  :obj:`Query` and :obj:`Table` for more information.


TODO:
    * Add status updates (node 5 / 7 complete) by using tqdm's
    * Does the chaining build up an AnalysisChain?
"""
from .utils import minify_sql


def _buffer(q_obj, dist):
    """Buffer a query or table"""
    if isinstance(q_obj, Query):
        query = q_obj.query
    else:
        query = query
    return '''
        SELECT
            ST_Buffer(the_geom, {dist}) as the_geom
        FROM (
            {source_query}
        ) as _w
    '''.format(
        dist=dist,
        source_query=query)


class AnalysisChain(object):
    """Build up an analysis chain a la Builder Analysis.

    AnalysisChain allows you to build up a chain of analyses which are applied
    sequentially to a source (query or table).

    Example:

    ::

        from cartoframes import AnalysisChain, Table
        bklyn_demog = table('brooklyn_demographics')

        chain = AnalysisChain(
            bklyn_demog,
            [
                ('buffer', 100.0),  # buffer by 1/10 of a kilometer
                ('join', {        # spatial join
                    'target': table('gps_pings')\
                                  .filter('type=cell')\
                                  .distinct(on='user_id'),
                    'on': 'the_geom',
                    'type': 'left'
                }),
                ('agg', {'by': 'geoid',  # aggregate points to polygons
                         'ops': [('count', 'num_gps_pings'),
                                 ('', '')]}),
                ('div', [('num_gps_pings', 'total_pop')])  # add new column to normalize point count
            ]
        )
        chain.compute()


    Parameters:

      source (str, :obj:`Table`, or :obj:`Query`): If str, the name of a table
        in user account. If :obj:`Table` or :obj:`Query`, the base data for the
        analysis chain.
      analyses (list): A list of analyses to apply to `source`. The following
        are available analyses and their parameters:

        - buffer:
          - radius (float, required): radius of buffer in meters
        - join:
          - target (:obj:`Table`, :obj:`Query`, or :obj:`str`): The data source
            that the `source` is joined against.
          - on (:obj:`str`): If a :obj:`str`, the column name to join on. If
            `the_geom` is provided, a spatial join will be performed. If a
            :obj:`tuple` is provided, the first element is the column from
            `source` which is matched to the second element, the column from
            `target`.

    """ # noqa
    def __init__(self, source, analyses):
        self.context = source.context
        self.analyses = analyses
        self.source = source
        self.final_query = None

    def _build_chain(self):
        """Builds up an analysis based on `analyses`"""
        temp = 'SELECT * FROM ({query}) as _w{n}'
        last = temp.format(query=self.source.query, n=0)
        for idx, analysis in enumerate(self.analyses):
            last = temp.format(
                query=analysis[0](last, *analysis[1]),
                n=idx+1
            )
        self.final_query = last

    def append(self, analysis):
        """Append a new analysis to a chain
        
        Example:

        ::

            chain = AnalysisChain(
                Table('transactions'),
                [('buffer', 10),
                 ('augment', 'median_income')]
            )
            chain.append(('knn', {'mean': 'median_income'}))

        Args:
          analysis (analysis): An analysis node
        """
        pass

    def compute(self):
        """Trigger the AnalysisChain to run

        Example:

        ::

            chain = AnalysisChain(...)
            # compute analysis chain
            df = chain.compute()
            # show results
            df.head()

        Returns:
            promise object, which reports the status of the analysis if not
            complete. Once the analysis finishes, the results will be returned
            if the operations were successful.
        """
        if self.final_query:
            return self.context.query(self.final_query)
        else:
            raise ValueError('No analysis nodes provided to analysis chain')


class Query(object):
    """:obj:`Query` gives a representation of a query in a users's CARTO
    account.

    Example:

    ::

        from cartoframes import CartoContext, Query
        cc = CartoContext()
        snapshot = Query('''
            SELECT
                count(*) as num_sightings,
                b.acadia_district_name,
                b.the_geom
            FROM
                bird_sightings as a, acadia_districts as b
            GROUP BY 2, 3
        ''')
        snapshot.local_moran('num_sightings', 5).filter('significance<=0.05')


    Parameters:

        context (:obj:`CartoContext`): :obj:`CartoContext` instance
          authenticated against the user's CARTO account.
        query (str): Valid query against user's CARTO account.
    """
    def __init__(self, context, query):
        self.query = query
        self.context = context

    def _validate_query(self, cols=None):
        """
        Validate that the query has the needed column names for the analysis
        to run
        """
        util_cols = ('cartodb_id', 'the_geom', 'the_geom_webmercator', )
        if cols is None:
            cols = util_cols
        self.context.query(
            'select {cols} FROM ({query}) as _w'.format(
                cols=','.join(cols),
                query=self.query
            )
        )

    def read(self):
        """Read the query to a pandas DataFrame

        Returns:
            pandas.DataFrame: Query represented as a pandas DataFrame
        """
        return self.context.query(self.query)

    def moran_local(self, colname, n_neighbors):
        """Local Moran's I

        Args:
          colname (:obj:`str`): Column name for performing Local Moran's I
            analysis on
        """
    def plot(self):
        """Plot all the columns in the query.

        Example:

        ::

            Query('''
                SELECT simpson_index, species
                FROM acadia_biodiversity
            ''').plot()
            <matplotlib plot>

        """
        return self.context.query(self.query).plot()

    def buffer(self, dist):
        """Buffer query
        Example:

        ::

            q = Query('...')
            buffered_q = q.buffer(150).compute()
            cc.map(layers=[buffered_q, q])

        Args:
            dist (float): Distance in meters to buffer a geometry
        """
        return Query(self.context, _buffer(self, dist))

    def describe(self, cols=None):
        """Gives back basic statistics for a table

        Args:
          cols (list of str): List of column names to get summary statistics

        TODO: add geometry information
        """
        if cols is None:
            cols = self.context.read(limit=0).columns
        qualities = ('count', 'avg', 'min', 'max', )
        summary_query = minify_sql((
            'SELECT {aggcols}',
            'FROM ({query}) as _w')).format(
                aggcols=('{agg}({col}) as {col}'.format(agg=None, col=None)),
                query=self.query)
        return self.context.query(summary_query)


class Table(Query):
    """Table object"""
    def __init__(self, table_name):
        """Table object"""
        super(Table, self).__init__('SELECT * FROM {}'.format(table_name))

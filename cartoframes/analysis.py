"""Spec-ing out the analysis framework for cartoframes"""


def buffer(q_obj, dist):
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
    """Build up an analysis chain à la Builder Analysis.

    AnalysisChain allows you to build up a chain of analyses which are applied
    sequentially to a source (query or table).

    Example:

    ::

        from cartoframes import analysischain, table
        bklyn_demog = table('brooklyn_demographics')

        chain = analysischain(
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


    Args:

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

    """
    def __init__(self, source, analyses):
        self.context = source.context
        self.analyses = analyses
        self.source = source
        self.final_query = None

    def build_chain(self):
        """Builds up an analysis based on `analyses`"""
        temp = 'SELECT * FROM ({query}) as _w{n}'
        last = temp.format(query=self.source.query, n=0)
        for idx, analysis in enumerate(self.analyses):
            last = temp.format(
                query=analysis[0](last, *analysis[1]),
                n=idx+1
            )
        self.final_query = last

    def compute(self):
        """Return the results of the analysis"""
        if self.final_query:
            return self.context.query(self.final_query)
        else:
            raise ValueError('No analysis nodes provided to analysis chain')


class Query(object):
    """`Query` gives a representation of a query in a users's CARTO account.
    
    
    
    """
    def __init__(self, context, query):
        self.query = query
        self.context = context

    def read(self):
        """read the query to a dataframe"""
        return self.context.query(self.query)

    def plot(self):
        """Plot all the columns in the query. cc.query(...).plot()"""

    def get(self):
        """get the query behind this object"""
        return self.query

    def buffer(self, dist):
        """buffer query"""
        return Query(self.context, buffer(self, dist))

    def describe(self, cols=None):
        """Gives back basic statistics for a table"""
        if cols is None:
            cols = self.read(limit=0).columns
        qualities = ('count', 'avg', 'min', 'max', )
        q = minify_sql((
            'SELECT {aggcols}',
            'FROM {table}')).format(
                aggcols=('{agg}({col}) as {col}'.format(agg=None, col=None)))
        return self.context.query(q)



class Table(Query):
    """Table object"""
    def __init__(self, table_name):
        """Table object"""
        super(Table, self).__init__('SELECT * FROM {}'.format(table_name))

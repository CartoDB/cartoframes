"""Table objects"""
from warnings import warn
from .layer import Layer, QueryLayer
from .utils import minify_sql

warn('entering')


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
    """Build up an analysis chain
    AnalysisChain allows you to build up a chain of analyses which are applied
    sequentially to a source (query or table).



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
    """`Query` gives a representation of a query in a users's CARTO account."""
    def __init__(self, context, query):
        self.query = query
        self.context = context

    def read(self):
        """read the query to a dataframe"""
        return self.context.query(self.query)

    def plot(self):
        """Plot all the columns in the query. cc.query(...).plot()"""
        self.context.query(self.query).plot()

    def get(self):
        """get the query behind this object"""
        return self.query

    def buffer(self, dist):
        """buffer query"""
        return Query(self.context, buffer(self, dist))

    def agg(self, aggs):
        """Performs an aggregation
        `aggs` is a list of tuples, like so:
            [('poverty_per_pop', 'max'),
             ('poverty_per_pop', 'min'),
             ('bike_commuter_rate', 'avg'), ]
        To add: countDistinct, avg, count, min, max, ...
        """
        print(aggs)
        return self.context.query(minify_sql((
            'SELECT {aggs}',
            '  FROM {table}',
        )).format(
            aggs=', '.join(
                '{agg}({col}) as {col}_{agg}'.format(agg=agg, col=col)
                for col, agg in aggs),
            table=self.table_name))

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

    def intersects(self, ref_table, not_intersects=True):
        """geometries from self which intersect with reference table"""
        self.context.sql_client.send('''
            DELETE FROM {table}
            WHERE {table}.cartodb_id {not_intersects} IN (
                SELECT {table}.cartodb_id
                FROM ({query}) as _w, {ref_table}
                WHERE ST_Intersects(_w.the_geom, {ref_table}.the_geom))
        '''.format(query=self.query,
                   ref_table=ref_table,
                   not_intersects='NOT' if not_intersects else ''))
        return self

    def layer(self):
        """return the layer object from this table layer"""
        return QueryLayer(self.query)


class Table(Query):
    """Table object"""
    def __init__(self, table_name):
        """Table object"""
        self.table_name = table_name
        super(Table, self).__init__('SELECT * FROM {}'.format(table_name))

    def layer(self):
        """return the layer object from this table layer"""
        return Layer(self.table_name)

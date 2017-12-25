"""Table objects"""
from warnings import warn
from .layer import Layer
from .utils import minify_sql

# TODO: mimic the code for Layer/QueryLayer/Etc
# Table should inherit from QueryLayer, for example


class Table(object):
    """Table object for interacting with at table on CARTO
    """
    def __init__(self, table_name, cc):
        self.table_name = table_name
        self.context = cc
        # TODO: is synced? is writable?
        # What other information should be stored?
        # geometry type?

    def read(self, limit=None):
        """Read a table into a dataframe"""
        return self.context.read(self.table_name, limit=limit)

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

    def buffer(self, dist):
        """Buffer geometry by `dist`"""
        self.context.sql_client.send('''
            UPDATE {table}
               SET the_geom = ST_Buffer(the_geom::geography, {dist})::geometry;
        '''.format(table=self.table_name,
                   dist=dist))
        return self

    def intersects(self, ref_table, not_intersects=True):
        """geometries from self which intersect with reference table"""
        self.context.sql_client.send('''
            DELETE FROM {table}
            WHERE {table}.cartodb_id {not_intersects} IN (
                SELECT {table}.cartodb_id
                FROM {table}, {ref_table}
                WHERE ST_Intersects({table}.the_geom, {ref_table}.the_geom))
        '''.format(table=self.table_name,
                   ref_table=ref_table,
                   not_intersects='NOT' if not_intersects else ''))
        return self

    def layer(self):
        """return the layer object from this table layer"""
        return Layer(self.table_name)

    # management
    def drop(self, *cols):
        """Drops columns in self.table"""
        geom_cols = set(('the_geom', 'the_geom_webmercator', ))
        if 'cartodb_id' in cols:
            raise ValueError('Cannot drop `cartodb_id` from CARTO table.')
        elif set(cols) & geom_cols:
            warn(
                'Dropping geometry columns `the_geom` and/or '
                '`the_geom_webmercator` means that maps will not be '
                'displayed.')
        query = minify_sql((
            'ALTER TABLE {table}',
            '{drops}'
        )).format(
            table=self.table_name,
            drops=', '.join('DROP COLUMN {col}' for col in cols))
        self.context.sql_client.send(query)

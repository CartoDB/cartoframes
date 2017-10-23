"""Table objects"""
from .layer import Layer

# TODO: mimic the code for Layer/QueryLayer/Etc
# Table should inherit from QueryLayer, for example

class Table(object):
    """Table object for interacting with at table on CARTO
    """
    def __init__(self, table_name, cc):
        self.table_name = table_name
        self.cc = cc
        # TODO: is synced? is writable?
        # What other information should be stored?
        # geometry type?

    def read(self):
        return self.cc.read(self.table_name)

    def buffer(self, dist):
        """Buffer geometry by `dist`"""
        self.cc.sql_client.send('''
            UPDATE {table}
               SET the_geom = ST_Buffer(the_geom::geography, {dist})::geometry;
        '''.format(table=self.table_name,
                   dist=dist))
        return self

    def intersects(self, ref_table, not_intersects=True):
        """geometries from self which intersect with reference table"""
        self.cc.sql_client.send('''
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
        return Layer(self.table_name)

from geopandas import GeoDataFrame

from ..utils.geom_utils import generate_index, generate_geometry


class CartoDataFrame(GeoDataFrame):
    def __init__(self, *args, **kwargs):
        """
        A CartoDataFrame object is a
        `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_
        that has a column with geometry. It extends the GeoDataFrame object to read and
        write data from CARTO, adding wrappers when necessary.
        """

        super(CartoDataFrame, self).__init__(*args, **kwargs)

    @staticmethod
    def from_carto(*args, **kwargs):
        """
        Alternate constructor to create a CartoDataFrame from a table or SQL query in CARTO.
        Equivalent to :py:meth:`read_carto <cartoframes.io.read_carto>`.
        """

        from ..io.carto import read_carto
        return read_carto(*args, **kwargs)

    @classmethod
    def from_file(cls, filename, **kwargs):
        """
        Alternate constructor to create a CartoDataFrame from a file.

        Examples:

            .. code::
                from cartoframes import CartoDataFrame

                cdf = CartoDataFrame.from_file('nybb.shp')
        """

        gdf = GeoDataFrame.from_file(filename, **kwargs)
        return cls(gdf)

    @classmethod
    def from_features(cls, features, **kwargs):
        gdf = GeoDataFrame.from_features(features, **kwargs)
        return cls(gdf)

    @staticmethod
    def to_carto(self, *args, **kwargs):
        """
        Upload a CartoDataFrame to CARTO.
        Equivalent to :py:meth:`to_carto <cartoframes.io.to_carto>`.

        Examples:

            .. code::
                cdf.to_carto(if_exists='replace')
        """

        from ..io.carto import to_carto
        return to_carto(self, *args, **kwargs)

    @staticmethod
    def convert(self, index_column=None, geom_column=None, lnglat_columns=None,
                drop_index=True, drop_geom=True, drop_lnglat=True):
        """
        Tries to decode the geometry automatically by looking for coordinates in columns.

        Examples:

            Decode the geometry automatically:

            .. code::
                cdf = CartoDataFrame(data).convert()

            Passing the geometry column explititely:

            .. code::
                cdf = CartoDataFrame(data)
                cdf.convert(geom_column='my_geom_column')
        """

        generate_index(self, index_column, drop_index)
        generate_geometry(self, geom_column, lnglat_columns, drop_geom, drop_lnglat)
        return self

    @staticmethod
    def visualize(self, *args, **kwargs):
        """
        Create a :py:class:`Map <cartoframes.viz.Map>`. visualization
        """
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))

    viz = visualize

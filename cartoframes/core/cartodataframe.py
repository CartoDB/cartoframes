from numpy import ndarray
from pandas import Series
from geopandas import GeoDataFrame, points_from_xy

from ..utils.geom_utils import decode_geometry_column


class CartoDataFrame(GeoDataFrame):
    """
    The CartoDataFrame class is an extension of the `geopandas.GeoDataFrame
    <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_ class. It provides
    powerful cartographic visualizations, geometry detection and decoding, and read / write
    access to the CARTO platform.
    """

    def __init__(self, data, *args, **kwargs):
        geometry = kwargs.get('geometry', None)
        if geometry is None:
            # Load geometry from data if not specified in kwargs
            if hasattr(data, 'geometry'):
                kwargs['geometry'] = data.geometry.name

        crs = kwargs.get('crs', None)
        if crs is None:
            # Load crs from data if not specified in kwargs
            if hasattr(data, 'crs'):
                kwargs['crs'] = data.crs

        super(CartoDataFrame, self).__init__(data, *args, **kwargs)

    @staticmethod
    def from_carto(*args, **kwargs):
        """
        Alternate constructor to create a CartoDataFrame from a table or SQL query in CARTO.
        It is needed to set up the :py:class:`cartoframes.auth.Credentials`.
        Equivalent to :py:meth:`read_carto <cartoframes.io.carto.read_carto>`.

        Examples:

            Using a table name:

            .. code::

                from cartoframes import CartoDataFrame
                from cartoframes.auth import Credentials

                creds = Credentials.from_file('creds.json')

                cdf = CartoDataFrame.from_carto('table_name', creds)

                # or

                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('creds.json')

                cdf = CartoDataFrame.from_carto('table_name')

            Using a SQL query:

            .. code::

                from cartoframes import CartoDataFrame
                from cartoframes.auth import Credentials

                creds = Credentials.from_file('creds.json')

                cdf = CartoDataFrame.from_carto('SELECT * FROM table_name WHERE value > 100', creds)

                # or

                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('creds.json')

                cdf = CartoDataFrame.from_carto('SELECT * FROM table_name WHERE value > 100')
        """
        from ..io.carto import read_carto
        return read_carto(*args, **kwargs)

    @classmethod
    def from_file(cls, filename, **kwargs):
        """
        Alternate constructor to create a CartoDataFrame from a Shapefile or GeoJSON file.
        Extends from the GeoDataFrame.from_file method.

        Examples:

            .. code::

                from cartoframes import CartoDataFrame

                cdf = CartoDataFrame.from_file('nybb.shp')
        """
        result = GeoDataFrame.from_file(filename, **kwargs)
        result.__class__ = cls
        return result

    @classmethod
    def from_features(cls, features, **kwargs):
        """
        Alternate constructor to create a CartoDataframe from GeoJSON features.
        Extends from the GeoDataFrame.from_features method.

        Examples:

            .. code::

                from cartoframes import CartoDataFrame

                cdf = CartoDataFrame.from_features([{
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                            'coordinates': [125.6, 10.1]
                        },
                    'properties': {
                    'name': 'Dinagat Islands'
                }])
        """
        result = GeoDataFrame.from_features(features, **kwargs)
        result.__class__ = cls
        return result

    def to_carto(self, *args, **kwargs):
        """
        Upload a CartoDataFrame to CARTO. It is needed to set up the
        :py:class:`cartoframes.auth.Credentials`.
        Equivalent to :py:meth:`to_carto <cartoframes.io.carto.to_carto>`.

        Examples:

            .. code::

                from cartoframes import CartoDataFrame
                from cartoframes.auth import Credentials

                creds = Credentials.from_file('creds.json')

                cdf = CartoDataFrame.from_file('nybb.shp')
                cdf.to_carto('table_name', creds, if_exists='replace')

                # or

                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('creds.json')

                cdf = CartoDataFrame.from_file('nybb.shp')
                cdf.to_carto('table_name', if_exists='replace')
        """
        from ..io.carto import to_carto
        return to_carto(self, *args, **kwargs)

    def viz(self, *args, **kwargs):
        """
        Creates a quick :py:class:`Map <cartoframes.viz.Map>` visualization. The parameters
        are passed directly to the Layer (style, popup, legend, widgets, etc.).

        Examples:

            .. code::

                from cartoframes import CartoDataFrame

                cdf = CartoDataFrame.from_file('world_population.geojson')

                cdf.viz()
        """
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))

    def has_geometry(self):
        """
        Method to check if the CartoDataFrame contains a valid geometry column or not.
        If there is no valid geometry, you can use the following methods:
        - set_geometry: to create a decoded geometry column from any raw geometry column.
        - set_geometry_from_xy: to create a geometry column from `longitude` and `latitude` columns.
        """
        return self._geometry_column_name in self

    def set_geometry(self, col, drop=False, inplace=False, crs=None):
        if inplace:
            frame = self
        else:
            frame = self.copy()

        # Decode geometry:
        #   WKB, EWKB, WKB_HEX, EWKB_HEX, WKB_BHEX, EWKB_BHEX, WKT, EWKT
        if isinstance(col, str) and col in frame:
            frame[col] = decode_geometry_column(frame[col])
        else:
            col = decode_geometry_column(col)

        # Call super set_geometry with decoded column
        super(CartoDataFrame, frame).set_geometry(col, drop=drop, inplace=True, crs=crs)

        if not inplace:
            return frame

    def set_geometry_from_xy(self, x, y, drop=False, inplace=False, crs=None):
        if isinstance(x, str) and x in self and isinstance(y, str) and y in self:
            x_col = self[x]
            y_col = self[y]
        else:
            x_col = x
            y_col = y

        # Generate geometry
        geom_col = points_from_xy(x_col, y_col)

        # Call super set_geometry with generated column
        frame = super(CartoDataFrame, self).set_geometry(geom_col, inplace=inplace, crs=crs)

        if drop:
            if frame is None:
                frame = self
            del frame[x]
            del frame[y]

        return frame

    @property
    def _constructor(self):
        return CartoDataFrame

    def __getitem__(self, key):
        result = super(self._constructor, self).__getitem__(key)
        if isinstance(key, (list, slice, ndarray, Series)):
            result.__class__ = self._constructor
        return result

    def __finalize__(self, *args, **kwargs):
        result = super(self._constructor, self).__finalize__(*args, **kwargs)
        result.__class__ = self._constructor
        return result

    def astype(self, *args, **kwargs):
        result = super(self._constructor, self).astype(*args, **kwargs)
        result.__class__ = self._constructor
        return result

    def merge(self, *args, **kwargs):
        result = super(self._constructor, self).merge(*args, **kwargs)
        result.__class__ = self._constructor
        return result

    def dissolve(self, *args, **kwargs):
        result = super(self._constructor, self).dissolve(*args, **kwargs)
        result.__class__ = self._constructor
        return result

    def explode(self, *args, **kwargs):
        result = super(self._constructor, self).explode(*args, **kwargs)
        result.__class__ = self._constructor
        return result

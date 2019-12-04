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
        Equivalent to :py:meth:`cartoframes.read_carto <cartoframes.io.carto.read_carto>`.

        Args:
            source (str): table name or SQL query.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                instance of Credentials (username, api_key, etc).
            limit (int, optional):
                The number of rows to download. Default is to download all rows.
            retry_times (int, optional):
                Number of time to retry the download in case it fails. Default is 3.
            schema (str, optional): prefix of the table. By default, it gets the
                `current_schema()` using the credentials.
            index_col (str, optional): name of the column to be loaded as index.
                It can be used also to set the index name.
            decode_geom (bool, optional): convert the "the_geom" column into a valid geometry column.

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
                    }
                }])
        """
        result = GeoDataFrame.from_features(features, **kwargs)
        result.__class__ = cls
        return result

    def to_carto(self, *args, **kwargs):
        """
        Upload a CartoDataFrame to CARTO. It is needed to set up the
        :py:class:`cartoframes.auth.Credentials`.
        Equivalent to :py:meth:`cartoframes.to_carto <cartoframes.io.carto.to_carto>`.

        Args:
            table_name (str): name of the table to upload the data.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                instance of Credentials (username, api_key, etc).
            if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.
            geom_col (str, optional): name of the geometry column of the dataframe.
            index (bool, optional): write the index in the table. Default is False.
            index_label (str, optional): name of the index column in the table. By default it
                uses the name of the index from the dataframe.

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

        Args:
            style (str, dict, or :py:class:`Style <cartoframes.viz.Style>`, optional):
                The style of the visualization.
            popup (dict or :py:class:`Popup <cartoframes.viz.Popup>`, optional):
                This option adds interactivity (click and hover) to a layer to show popups.
                The columns to be shown must be added in a list format for each event.
                See :py:class:`Popup <cartoframes.viz.Popup>` for more information.
            legend (dict or :py:class:`Legend <cartoframes.viz.Legend>`, optional):
                The legend definition for a layer. It contains the information
                to show a legend "type" (``color-category``, ``color-bins``,
                ``color-continuous``), "prop" (color) and also text information:
                "title", "description" and "footer". See :py:class:`Legend
                <cartoframes.viz.Legend>` for more information.
            widgets (dict, list, or :py:class:`WidgetList <cartoframes.viz.WidgetList>`, optional):
                Widget or list of widgets for a layer. It contains the information to display
                different widget types on the top right of the map. See
                :py:class:`WidgetList` for more information.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. This is only used for the simplified Source API.
                When a :py:class:`Source <cartoframes.viz.Source>` is passed as source,
                these credentials is simply ignored. If not provided the credentials will be
                automatically obtained from the default credentials.
            bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
                keys, or an array of floats in the following structure: [[west,
                south], [east, north]]. If not provided the bounds will be automatically
                calculated to fit all features.
            geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.


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
        Method to check if the CartoDataFrame contains a valid geometry column.
        If there is no valid geometry, you can use the following methods:

            - `set_geometry`: to create a decoded geometry column from any raw geometry column.
            - `set_geometry_from_xy`: to create a geometry column from `longitude` and `latitude` columns.
        """
        return self._geometry_column_name in self

    def set_geometry(self, col, drop=False, inplace=False, crs=None):
        """
        Set the CartoDataFrame geometry using either an existing column or the specified input.
        By default yields a new object. The original geometry column is replaced with the input.
        It detects the geometry encoding and it decodes the column if required. Supported geometry
        encodings are:

            - `WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
            - `Extended WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
            - `WKT` (String)
            - `Extended WKT` (String)

        Args:
            col (column label or array): Name of the column or column containing the geometry.
            drop (boolean, default False): Delete the column to be used as the new geometry.
            inplace (boolean, default False): Modify the CartoDataFrame in place (do not create a new object).
            crs (str/result of fion.get_crs, optional): Coordinate system to use. If passed, overrides both
                DataFrame and col's crs. Otherwise, tries to get crs from passed col values or DataFrame.

        Examples:

            .. code::

                cdf.set_geometry('the_geom', drop=True, inplace=True)
        """
        if inplace:
            frame = self
        else:
            frame = self.copy()

        # Decode geometry
        if isinstance(col, str) and col in frame:
            frame[col] = decode_geometry_column(frame[col])
        else:
            col = decode_geometry_column(col)

        # Call super set_geometry with decoded column
        super(CartoDataFrame, frame).set_geometry(col, drop=drop, inplace=True, crs=crs)

        if not inplace:
            return frame

    def set_geometry_from_xy(self, x, y, drop=False, inplace=False, crs=None):
        """
        Set the CartoDataFrame geometry using either existing lng/lat columns or the specified inputs.
        By default yields a new object. The original geometry column is replaced with the new one.

        Args:
            x (column label or array): Name of the x (longitude) column or column containing the x coordinates.
            y (column label or array): Name of the y (latitude) column or column containing the y coordinates.
            drop (boolean, default False): Delete the columns to be used to generate the new geometry.
            inplace (boolean, default False): Modify the CartoDataFrame in place (do not create a new object).
            crs (str/result of fion.get_crs, optional): Coordinate system to use. If passed, overrides both
                DataFrame and col's crs. Otherwise, tries to get crs from passed col values or DataFrame.

        Examples:

            .. code::

                cdf.set_geometry_from_xy('lng', 'lat', drop=True, inplace=True)
        """
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

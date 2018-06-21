"""Layer classes for map creation. See examples in `layer.Layer
<#layer.Layer>`__ and `layer.QueryLayer <#layer.QueryLayer>`__
for example usage for data layers. See `layer.BaseMap <#layer.BaseMap>`__ for
basemap layers.
"""
from __future__ import absolute_import
import pandas as pd
import webcolors

from .utils import cssify, join_url, minify_sql
from .styling import BinMethod, mint, antique, get_scheme_cartocss

# colors map data layers without color specified
# from CARTOColor vivid scheme
DEFAULT_COLORS = ('#E58606', '#5D69B1', '#52BCA3', '#99C945', '#CC61B0',
                  '#24796C', '#DAA51B', '#2F8AC4', '#764E9F', '#ED645A',
                  '#CC3A8E', '#A5AA99')


class AbstractLayer(object):
    """Abstract Layer object"""
    is_basemap = False

    def __init__(self):
        pass

    def _setup(self, layers, layer_idx):
        pass


class BaseMap(AbstractLayer):
    """Layer object for adding basemaps to a cartoframes map.

    Example:
        Add a custom basemap to a cartoframes map.
    .. code:: python

        import cartoframes
        from cartoframes import BaseMap, Layer
        cc = cartoframes.CartoContext(BASEURL, APIKEY)
        cc.map(layers=[BaseMap(source='light', labels='front'),
                       Layer('acadia_biodiversity')])

    Args:
        source (str, optional): One of ``light`` or ``dark``. Defaults to
            ``voyager``. Basemaps come from
            https://carto.com/location-data-services/basemaps/
        labels (str, optional): One of ``back``, ``front``, or None. Labels on
            the front will be above the data layers. Labels on back will be
            underneath the data layers but on top of the basemap. Setting
            labels to ``None`` will only show the basemap.
        only_labels (bool, optional): Whether to show labels or not.

    """
    is_basemap = True

    def __init__(self, source='voyager', labels='back', only_labels=False):
        if labels not in ('front', 'back', None):
            raise ValueError("labels must be None, 'front', or 'back'")

        self.source = source
        self.labels = labels
        self.only_labels = only_labels
        stem = 'https://{s}.basemaps.cartocdn.com/rastertiles/'

        if self.is_basic():
            if only_labels:
                style = source + '_only_labels'
            else:
                if source in ('dark', 'light', ):
                    label_type = '_all'
                else:
                    label_type = '_labels_under'
                style = source + (label_type if labels == 'back'
                                  else '_nolabels')
            self.url = join_url(stem, style, '{z}/{x}/{y}.png')
        elif self.source.startswith('http'):
            # TODO: Remove this once baselayer urls can be passed in named
            # map config
            raise ValueError('BaseMap cannot contain a custom url at the '
                             'moment')
            # self.url = source
        else:
            raise ValueError("`source` must be one of 'dark', 'light', or "
                             "'voyager'")

    def __repr__(self):
        """String representation of object"""
        return 'BaseMap(source={0}, labels={1}, only_labels={2})'.format(
            self.source, self.labels, self.only_labels)

    def is_basic(self):
        """Does BaseMap pull from CARTO default basemaps?

        Returns:
            bool: `True` if using a CARTO basemap (Dark Matter, Positron or
            Voyager), `False` otherwise.
        """
        return self.source in ('dark', 'light', 'voyager', )


class QueryLayer(AbstractLayer):
    """cartoframes data layer based on an arbitrary query to the user's CARTO
    database. This layer class is useful for offloading processing to the cloud
    to do some of the following:

    * Visualizing spatial operations using `PostGIS <http://postgis.net/>`__
      and `PostgreSQL <https://www.postgresql.org/>`__, which is the database
      underlying CARTO
    * Performing arbitrary relational database queries (e.g., complex JOINs
      in SQL instead of in pandas)
    * Visualizing a subset of the data (e.g., ``SELECT * FROM table LIMIT
      1000``)

    Used in the `layers` keyword in :py:meth:`CartoContext.map
    <cartoframes.context.CartoContext.map>`.

    Example:
        Underlay a QueryLayer with a complex query below a layer from a table.
        The QueryLayer is colored by the calculated column ``abs_diff``, and
        points are sized by the column ``i_measure``.

    .. code:: python

        import cartoframes
        from cartoframes import QueryLayer, styling
        cc = cartoframes.CartoContext(BASEURL, APIKEY)
        cc.map(layers=[QueryLayer('''
                                  WITH i_cte As (
                                    SELECT
                                        ST_Buffer(the_geom::geography, 500)::geometry As the_geom,
                                        cartodb_id,
                                        measure,
                                        date
                                      FROM interesting_data
                                     WHERE date > '2017-04-19'
                                  )
                                  SELECT
                                     i.cartodb_id, i.the_geom,
                                     ST_Transform(i.the_geom, 3857) AS the_geom_webmercator,
                                     abs(i.measure - j.measure) AS abs_diff,
                                     i.measure AS i_measure
                                    FROM i_cte AS i
                                    JOIN awesome_data AS j
                                      ON i.event_id = j.event_id
                                   WHERE j.measure IS NOT NULL
                                     AND j.date < '2017-04-29'
                                  ''',
                                  color={'column': 'abs_diff',
                                         'scheme': styling.sunsetDark(7)},
                                  size='i_measure'),
                       Layer('fantastic_sql_table')])

    Args:
        query (str): Query to expose data on a map layer. At a minimum, a
            query needs to have the columns `cartodb_id`, `the_geom`, and
            `the_geom_webmercator` for the map to display. Read more about
            queries in `CARTO's docs
            <https://carto.com/docs/tips-and-tricks/geospatial-analysis>`__.

        time (dict or str, optional): Time-based style to apply to layer.

            If `time` is a :obj:`str`, it must be the name of a column which
            has a data type of `datetime` or `float`.

            .. code::

                from cartoframes import QueryLayer
                l = QueryLayer('SELECT * FROM acadia_biodiversity',
                               time='bird_sighting_time')

            If `time` is a :obj:`dict`, the following keys are options:

            - column (`str`, required): Column for animating map, which must
              be of type `datetime` or `float`.
            - method (`str`, optional): Type of aggregation method for
              operating on `Torque TileCubes
              <https://github.com/CartoDB/torque>`__. Must be one of ``avg``,
              ``sum``, or another `PostgreSQL aggregate functions
              <https://www.postgresql.org/docs/9.5/static/functions-aggregate.html>`__
              with a numeric output. Defaults to ``count``.
            - cumulative (:obj:`bool`, optional): Whether to accumulate points over
              time (``True``) or not (``False``, default)
            - frames (`int`, optional): Number of frames in the animation.
              Defaults to 256.
            - duration (`int`, optional): Number of seconds in the animation.
              Defaults to 30.
            - trails (`int`, optional): Number of trails after the incidence of
              a point. Defaults to 2.

            .. code::

                from cartoframes import Layer
                l = Layer('acadia_biodiversity',
                          time={
                              'column': 'bird_sighting_time',
                              'cumulative': True,
                              'frames': 128,
                              'duration': 15
                          })

        color (dict or str, optional): Color style to apply to map. For
            example, this can be used to change the color of all geometries
            in this layer, or to create a graduated color or choropleth map.

            If `color` is a :obj:`str`, there are two options:

            - A column name to style by to create, for example, a choropleth
              map if working with polygons. The default classification is
              `quantiles` for quantitative data and `category` for
              qualitative data.
            - A hex value or `web color name
              <https://www.w3.org/TR/css3-color/#svg-color>`__.

            .. code::

                # color all geometries red (#F00)
                from cartoframes import Layer
                l = Layer('acadia_biodiversity',
                          color='red')

                # color on 'num_eggs' (using defalt color scheme and quantification)
                l = Layer('acadia_biodiversity',
                          color='num_eggs')

            If `color` is a :obj:`dict`, the following keys are options, with
            values described:

            - column (`str`): Column used for the basis of styling
            - scheme (`dict`, optional): Scheme such as `styling.sunset(7)`
              from the `styling module <#module-styling>`__ of cartoframes that
              exposes `CARTOColors
              <https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names>`__.
              Defaults to `mint <#styling.mint>`__ scheme for quantitative
              data and `bold` for qualitative data. More control is given by
              using `styling.scheme <#styling.scheme>`__.

              If you wish to define a custom scheme outside of CARTOColors, it
              is recommended to use the `styling.custom <#styling.custom>`__
              utility function.

            .. code::

                from cartoframes import QueryLayer, styling
                l = QueryLayer('SELECT * FROM acadia_biodiversity',
                               color={
                                   'column': 'simpson_index',
                                   'scheme': styling.mint(7, bin_method='equal')
                               })

        size (dict or int, optional): Size style to apply to point data.

            If `size` is an :obj:`int`, all points are sized by this value.

            .. code::

                from cartoframes import QueryLayer
                l = QueryLayer('SELECT * FROM acadia_biodiversity',
                               size=7)

            If `size` is a :obj:`str`, this value is interpreted as a column,
            and the points are sized by the value in this column. The
            classification method defaults to `quantiles`, with a min size of
            5, and a max size of 5. Use the :obj:`dict` input to override these
            values.

            .. code::

                from cartoframes import Layer
                l = Layer('acadia_biodiversity',
                          size='num_eggs')

            If `size` is a :obj:`dict`, the follow keys are options, with
            values described as:

            - column (`str`): Column to base sizing of points on
            - bin_method (`str`, optional): Quantification method for dividing
              data range into bins. Must be one of the methods in
              :obj:`BinMethod` (excluding `category`).
            - bins (`int`, optional): Number of bins to break data into.
              Defaults to 5.
            - max (`int`, optional): Maximum point width (in pixels). Defaults
              to 25.
            - min (`int`, optional): Minimum point width (in pixels). Defaults
              to 5.

            .. code::

                from cartoframes import Layer
                l = Layer('acadia_biodiversity',
                          size={
                              'column': 'num_eggs',
                              'max': 10,
                              'min': 2
                          })

        opacity (float, optional): Opacity of layer from 0 to 1. Defaults to
          0.9.
        tooltip (tuple, optional): **Not yet implemented.**
        legend: **Not yet implemented.**

    Raises:

        CartoException: If a column name used in any of the styling options is
          not in the data source in `query` (or `table` if using :obj:`Layer`).
        ValueError: If styling using a :obj:`dict` and a ``column`` key is not
          present, or if the data type for a styling option is not supported.
          This is also raised if styling by a geometry column (i.e.,
          ``the_geom`` or ``the_geom_webmercator``). Futher, this is raised if
          requesting a time-based map with a data source that has geometries
          other than points.
    """  # noqa
    def __init__(self, query, time=None, color=None, size=None, opacity=None,
                 tooltip=None, legend=None):

        self.query = query
        self.orig_query = query
        # style_cols and geom_type are updated right before layer is `_setup`
        # style columns as keys, data types as values
        self.style_cols = dict()
        self.geom_type = None
        self.cartocss = None
        self.torque_cartocss = None

        # TODO: move these if/else branches to individual methods
        # color, scheme = self._get_colorscheme()
        # time = self._get_timescheme()
        # size = self._get_sizescheme()
        # If column was specified, force a scheme
        # It could be that there is a column named 'blue' for example
        if isinstance(color, dict):
            if 'column' not in color:
                raise ValueError("Color must include a 'column' value")
            # get scheme if exists. if not, one will be chosen later if needed
            scheme = color.get('scheme')
            color = color['column']
            self.style_cols[color] = None
        elif (color and
              color[0] != '#' and
              color not in webcolors.CSS3_NAMES_TO_HEX):
            # color specified that is not a web color or hex value so its
            #  assumed to be a column name
            color = color
            self.style_cols[color] = None
            scheme = None
        else:
            # assume it's a color (hex, rgb(...),  or webcolor name)
            color = color
            scheme = None

        if time:
            if isinstance(time, dict):
                if 'column' not in time:
                    raise ValueError("`time` must include a 'column' "
                                     "key/value")
                time_column = time['column']
                time_options = time
            elif isinstance(time, str):
                time_column = time
                time_options = {}
            else:
                raise ValueError('`time` should be a column name or '
                                 'dictionary of styling options.')

            self.style_cols[time_column] = None
            time = {
                'column': time_column,
                'method': 'count',
                'cumulative': False,
                'frames': 256,
                'duration': 30,
                'trails': 2,
            }
            time.update(time_options)

        # assign size defaults if size is not specified
        if time:
            size = size or 4
        else:
            size = size or 10
        if isinstance(size, str):
            size = {'column': size}
        if isinstance(size, dict):
            if 'column' not in size:
                raise ValueError("`size` must include a 'column' key/value")
            if time:
                raise ValueError("When time is specified, size can "
                                 "only be a fixed size")
            old_size = size
            # Default size range, bins, and bin_method
            size = {
                'range': [5, 25],
                'bins': 5,
                'bin_method': BinMethod.quantiles,
            }
            # Assign default range and update if min/max given
            old_size['range'] = old_size.get('range', size['range'])
            if 'min' in old_size:
                old_size['range'][0] = old_size['min']
                old_size.pop('min')
            if 'max' in old_size:
                old_size['range'][1] = old_size['max']
                old_size.pop('max')
            # Update all the keys in size if they exist in old_size
            size.update(old_size)
            self.style_cols[size['column']] = None

        self.color = color
        self.opacity = opacity if opacity is not None else 0.9
        self.scheme = scheme
        self.size = size
        self.time = time
        self.tooltip = tooltip
        self.legend = legend
        self._validate_columns()

    def _validate_columns(self):
        """Validate the options in the styles"""
        geom_cols = {'the_geom', 'the_geom_webmercator', }
        col_overlap = set(self.style_cols) & geom_cols
        if col_overlap:
            raise ValueError('Style columns cannot be geometry '
                             'columns. `{col}` was chosen.'.format(
                                 col=','.join(col_overlap)))

    def _setup(self, layers, layer_idx):
        basemap = layers[0]

        # if color not specified, choose a default
        # choose color time default
        if self.time:
            # default torque color
            self.color = self.color or '#2752ff'
        else:
            self.color = self.color or DEFAULT_COLORS[layer_idx]
        # choose appropriate scheme if not already specified
        if (not self.scheme) and (self.color in self.style_cols):
            if self.style_cols[self.color] in ('string', 'boolean', ):
                self.scheme = antique(10)
            elif self.style_cols[self.color] in ('number', ):
                self.scheme = mint(5)
            elif self.style_cols[self.color] in ('date', 'geometry', ):
                raise ValueError(
                    'Cannot style column `{col}` of type `{type}`. It must be '
                    'numeric, text, or boolean.'.format(
                        col=self.color, type=self.style_cols[self.color]))

        if self.time:
            # validate time column information
            if self.geom_type != 'point':
                raise ValueError('Cannot do time-based maps with data in '
                                 '`{query}` since this table does not contain '
                                 'point geometries'.format(
                                     query=self.orig_query))
            elif self.style_cols[self.time['column']] not in (
                    'number', 'date', ):
                raise ValueError('Cannot create an animated map from column '
                                 '`{col}` because it is of type {t1}. It must '
                                 'be of type number or date.'.format(
                                     col=self.time['column'],
                                     t1=self.style_cols[self.time['column']]))

            # don't use turbo-carto for animated maps
            column = self.time['column']
            frames = self.time['frames']
            method = self.time['method']
            duration = self.time['duration']
            if (self.color in self.style_cols and
                    self.style_cols[self.color] in ('string', 'boolean', )):
                self.query = minify_sql([
                    'SELECT',
                    '    orig.*, __wrap.cf_value_{col}',
                    'FROM ({query}) AS orig, (',
                    '    SELECT',
                    '      row_number() OVER (',
                    '        ORDER BY val_{col}_cnt DESC) AS cf_value_{col},',
                    '      {col}',
                    '    FROM (',
                    '        SELECT {col}, count({col}) AS val_{col}_cnt',
                    '        FROM ({query}) as orig',
                    '        GROUP BY {col}',
                    '        ORDER BY 2 DESC',
                    '    ) AS _wrap',
                    ') AS __wrap',
                    'WHERE __wrap.{col} = orig.{col}',
                ]).format(col=self.color, query=self.orig_query)
                agg_func = '\'CDB_Math_Mode(cf_value_{})\''.format(self.color)
                self.scheme = {
                    'bins': [str(i) for i in range(1, 11)],
                    'name': (self.scheme.get('name') if self.scheme
                             else 'Bold'),
                    'bin_method': '', }
            elif (self.color in self.style_cols and
                  self.style_cols[self.color] in ('number', )):
                self.query = ' '.join([
                    'SELECT *, {col} as value',
                    'FROM ({query}) as _wrap'
                ]).format(col=self.color, query=self.orig_query)
                agg_func = '\'avg({})\''.format(self.color)
            else:
                agg_func = "'{method}(cartodb_id)'".format(
                    method=method)
            self.torque_cartocss = cssify({
                'Map': {
                    '-torque-frame-count': frames,
                    '-torque-animation-duration': duration,
                    '-torque-time-attribute': "'{}'".format(column),
                    '-torque-aggregation-function': agg_func,
                    '-torque-resolution': 1,
                    '-torque-data-aggregation': ('cumulative'
                                                 if self.time['cumulative']
                                                 else 'linear'),
                },
            })
            self.cartocss = (self.torque_cartocss
                             + self._get_cartocss(basemap, has_time=True))
        else:
            # use turbo-carto for non-animated maps
            self.cartocss = self._get_cartocss(basemap)

    def _get_cartocss(self, basemap, has_time=False):
        """Generate cartocss for class properties"""
        if isinstance(self.size, int):
            size_style = self.size or 4
        elif isinstance(self.size, dict):
            size_style = ('ramp([{column}],'
                          ' range({min_range},{max_range}),'
                          ' {bin_method}({bins}))').format(
                              column=self.size['column'],
                              min_range=self.size['range'][0],
                              max_range=self.size['range'][1],
                              bin_method=self.size['bin_method'],
                              bins=self.size['bins'])

        if self.scheme:
            color_style = get_scheme_cartocss(
                'value' if has_time else self.color,
                self.scheme)
        else:
            color_style = self.color

        line_color = '#000' if basemap.source == 'dark' else '#FFF'
        if self.time:
            css = cssify({
                # Torque Point CSS
                "#layer": {
                    'marker-width': size_style,
                    'marker-fill': color_style,
                    'marker-fill-opacity': self.opacity,
                    'marker-allow-overlap': 'true',
                    'marker-line-width': 0,
                    'marker-line-color': line_color,
                    'marker-line-opacity': 1,
                    'comp-op': 'source-over',
                }
            })
            if self.color in self.style_cols:
                css += cssify({
                    '#layer[{} = null]'.format(self.color): {
                        'marker-fill': '#666'}
                    })
            for trail_num in range(1, self.time['trails'] + 1):
                # Trails decay as 1/2^n, and grow 30% at each step
                trail_temp = cssify({
                    '#layer[frame-offset={}]'.format(trail_num): {
                        'marker-width': size_style * (1.0 + trail_num * 0.3),
                        'marker-opacity': 0.9 / 2.0**trail_num,
                    }
                })
                css += trail_temp
            return css
        else:
            if self.geom_type == 'point':
                css = cssify({
                    # Point CSS
                    "#layer": {
                        'marker-width': size_style,
                        'marker-fill': color_style,
                        'marker-fill-opacity': self.opacity,
                        'marker-allow-overlap': 'true',
                        'marker-line-width': '0.5',
                        'marker-line-color': line_color,
                        'marker-line-opacity': '1',
                    }})
                if self.color in self.style_cols:
                    css += cssify({
                        '#layer[{} = null]'.format(self.color): {
                            'marker-fill': '#ccc'}
                        })
                return css
            elif self.geom_type == 'line':
                css = cssify({
                    "#layer": {
                        'line-width': '1.5',
                        'line-color': color_style,
                        'line-opacity': self.opacity
                    }})
                if self.color in self.style_cols:
                    css += cssify({
                        '#layer[{} = null]'.format(self.color): {
                            'line-color': '#ccc'}
                        })
                return css
            elif self.geom_type == 'polygon':
                css = cssify({
                    "#layer": {
                        'polygon-fill': color_style,
                        'polygon-opacity': self.opacity,
                        'polygon-gamma': '0.5',
                        'line-color': '#FFF',
                        'line-width': '0.5',
                        'line-opacity': '0.25',
                        'line-comp-op': 'hard-light',
                    }})
                if self.color in self.style_cols:
                    css += cssify({
                        '#layer[{} = null]'.format(self.color): {
                            'polygon-fill': '#ccc'}
                        })
                return css
            else:
                raise ValueError('Unsupported geometry type: {}'.format(
                    self.geom_type))


class Layer(QueryLayer):
    """A cartoframes Data Layer based on a specific table in user's CARTO
    database. This layer class is used for visualizing individual datasets
    with :py:meth:`CartoContext.map
    <cartoframes.context.CartoContext.map>`\'s `layers`
    keyword argument.

    Example:

        .. code:: python

            import cartoframes
            from cartoframes import QueryLayer, styling
            cc = cartoframes.CartoContext(BASEURL, APIKEY)
            cc.map(layers=[Layer('fantastic_sql_table',
                                 size=7,
                                 color={'column': 'mr_fox_sightings',
                                        'scheme': styling.prism(10)})])

    Args:
        table_name (str): Name of table in CARTO account
        Styling: See :py:class:`QueryLayer <cartoframes.layer.QueryLayer>`
        for a full list of all arguments arguments for styling this map data
        layer.
        source (pandas.DataFrame, optional): Not currently implemented
        overwrite (bool, optional): Not currently implemented
    """
    def __init__(self, table_name, source=None, overwrite=False, time=None,
                 color=None, size=None, opacity=None, tooltip=None,
                 legend=None):

        self.table_name = table_name
        self.source = source
        self.overwrite = overwrite

        super(Layer, self).__init__('SELECT * FROM {}'.format(table_name),
                                    time=time,
                                    color=color,
                                    size=size,
                                    opacity=opacity,
                                    tooltip=tooltip,
                                    legend=legend)

    def _setup(self, layers, layer_idx):
        if isinstance(self.source, pd.DataFrame):
            raise NotImplementedError('Not currently implemented')
            # context.write(self.source,
            #               self.table_name,
            #               overwrite=self.overwrite)
        super(Layer, self)._setup(layers, layer_idx)

# cdb_context.map([BaseMap('light'),
#                  BaseMap('dark'),
#                  BaseMap('https://{x}/{y}/{z}'),
#                  BaseMap('light', labels=[default: 'back', 'front', 'back',
#                                           None]),
#                  Layer('mydata',
#                        time_column='timestamp'),
#                  Layer('foo', df,
#                        time_column='timestamp',
#                        color='col1',
#                        size=10),
#                  Layer(df,
#                        time_column='timestamp',
#                        color='col1',
#                        size=10,
#                        style={
#                            'column': 'col1',
#                            'scheme': cartoframes.styling.mint(5),
#                            'size': 10, # Option 1, fixed size
#                            'size': 'col2', # Option 2, by value Error if
#                                              using time_column
#                            'size': {
#                                'column': 'col2', # Error if using time_column
#                                'range': (1, 10),
#                                'bins': 10,
#                                'bin_method': cartoframes.BinMethod.quantiles,
#                            },
#                            'time': {
#                                'column': 'foo',
#                                'method': 'avg',
#                                'cumulative': False,
#                                'frames': 256,
#                                'duration': 30,
#                            },
#                            'tooltip': 'col1',
#                            'tooltip': ['col1', 'col2'],
#                            'legend': 'col1',
#                            'legend': ['col1', 'col2'],
#                            'widgets': 'col1',
#                            'widgets': ['col1', 'col2'],
#                            'widgets': {
#                                'col1':
#                                 cartoframes.widgets.Histogram(use_global=True),
#                                'col2': cartoframes.widgets.Category(),
#                                'col3': cartoframes.widgets.Min(),
#                                'col4': cartoframes.widgets.Max(),
#                            },
#                        })
#                  QueryLayer('select * from foo',
#                             time_column='timestamp'),

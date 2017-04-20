import itertools
import pandas as pd
import random
import webcolors
from cartoframes.utils import cssify
from cartoframes.styling import BinMethod, mint, get_scheme_cartocss


DEFAULT_COLORS = ['#F9CA34', '#4ABD9A', '#4A5798', '#DF5E26',
                  '#F9CA34', '#4ABD9A', '#4A5798', '#DF5E26']


class AbstractLayer:
    """Abstract Layer object"""
    is_basemap = False

    def __init__(self):
        pass

    def _setup(self, context, layers, layer_idx):
        pass


class BaseMap(AbstractLayer):
    """Layer object for adding basemaps to a cartoframes map.

    Example:
        Add a custom basemap to a cartoframes map.
        ::

            import cartoframes
            from cartoframes import BaseMap, Layer
            cc = cartoframes.CartoContext(BASEURL, APIKEY)
            cc.map(layers=[BaseMap(source='light', labels='front'),
                           Layer('acadia_biodiversity')])

    Args:
        source (str, optional): One of ``light`` or ``dark``. Defaults to ``dark``.
            Basemaps come from
            https://carto.com/location-data-services/basemaps/
        labels (str, optional): One of ``back``, ``front``, or None. Labels on the
            front will be above the data layers. Labels on back will be
            underneath the data layers but on top of the basemap. Setting
            labels to ``None`` will only show the basemap.
        only_labels (bool, optional): Whether to show labels or not.

    """
    is_basemap = True

    def __init__(self, source='dark', labels='back', only_labels=False):
        if labels not in ['front', 'back', None]:
            raise ValueError("labels must be None, 'front', or 'back'")

        self.source = source
        self.labels = labels

        if self.is_basic():
            if not only_labels:
                style = source + ('_all' if labels == 'back' else '_nolabels')
            else:
                style = source + '_only_labels'
            self.url = ('https://cartodb-basemaps-{{s}}.global.ssl.fastly.net/'
                        '{style}/{{z}}/{{x}}/{{y}}.png').format(style=style)
        elif self.source.startswith('http'):
            # [BUG] Remove this once baselayer urls can be passed in named map config
            raise ValueError('BaseMap cannot contain a custom url at the '
                             'moment')
            # self.url = source
        else:
            raise ValueError("`source` must be one of 'dark' or 'light'")

    def is_basic(self):
        """Does BaseMap pull from CARTO default basemaps?"""
        return self.source in ('dark', 'light')


class QueryLayer(AbstractLayer):
    """cartoframes Data Layer based on an arbitrary query to the user's CARTO
    database. This layer class is useful for offloading processing to the cloud
    to do some of the following:

    * pull down a snapshot of the data (e.g., selecting only important columns
    instead of all columns in the dataset)
    * doing spatial processing using `PostGIS <http://postgis.net/>`__ and
    `PostgreSQL <https://www.postgresql.org/>`__, which is the database
    underlying CARTO
    * performing arbitrary relational database queries (e.g., complex JOINs
    in SQL instead of in pandas)

    Example:
    ::

        import cartoframes
        from cartoframes import QueryLayer
        cc = cartoframes.CartoContext(BASEURL, APIKEY)
        cc.map(layers=[QueryLayer('''
                                  SELECT
                                      cartodb_id, the_geom,
                                      the_geom_webmercator,
                                      abs(i.measure- j.measure) as abs_diff,
                                  FROM interesting_data AS i
                                  JOIN awesome_data AS j
                                    ON i.event_id = j.event_id
                                  WHERE j.measure IS NOT NULL
                                    AND i.date > '2017-04-19'
                                  ''',
                                  color={'column': 'abs_diff',
                                         'scheme': 'SunsetDark'}),
                       Layer('fantastic_sql_table')])

    Args:
        query (str): Query to create a pandas DataFrame from. At a minimum, all
            queries need to have the columns `cartodb_id`, `the_geom`, and
            `the_geom_webmercator`. Read more in
            `CARTO's docs <https://carto.com/docs/tips-and-tricks/geospatial-analysis>`__.
        time (dict or str): Style to apply to layer.
            If `time` is a `dict`, the following keys are options:
            - column (str, required): Column for animating map from. Data must
            be of type time or float.
            - method (str, optional): Type of aggregation method for operating
            on `Torque TileCubes <https://github.com/CartoDB/torque>`__. Must
            be one of ``avg``, ``sum``, or another `PostgreSQL aggregate functions
            <https://www.postgresql.org/docs/9.5/static/functions-aggregate.html>`__
            with a numeric output. Defaults to ``count``.
            - cumulative (str, optional): Whether to accumulate (``cumulative``)
            the point data overtime, or show the event at the specified time
            only (``linear``). Defaults to ``linear``.
            - frames (int, optional): Number of frames in the animation.
            Defaults to 256.
            - duration (int, optional): Number of seconds in the animation.
            Defaults to 30.
            If `time` is a ``str``, then it must be a column name available in
            the query that is of type numeric or datetime.
        color (dict or str, optional): Color style to apply to map.
            If `color` is a ``dict``, the following keys are options, with
            values described:
            - column (str): Column to base coloring from.
            - scheme (str, optinal): Color scheme from
                `CartoColors
                <https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names>`__.
                Defaults to `Mint`.
            - bin_method (str, optional): Quantification method for dividing
                data range into bins. Must be one of: ``quantiles``, ``equal``,
                ``headtails`, or ``jenks``. Defaults to ``quantiles``.
            - bins (int, optional): Number of bins to divide data amongst in
                the `bin_method`. Defaults to 5.
    """
    def __init__(self, query, time=None, color=None, size=None,
                 tooltip=None, legend=None):

        self.query = query

        # redundant?
        color = color or None

        # If column was specified, force a scheme
        # It could be that there is a column named 'blue' for example
        if isinstance(color, dict):
            if 'column' not in color:
                raise ValueError("color must include a 'column' value")
            scheme = color.get('scheme', mint(5))
            color = color['column']
        elif (color and
              color[0] != '#' and
              color not in webcolors.CSS3_NAMES_TO_HEX):
            color = color
            scheme = mint(5)
        else:
            color  = color
            scheme = None

        if time:
            if isinstance(time, dict):
                if 'column' not in time:
                    raise ValueError("time must include a 'column' value")
                time_column = time['column']
                time_options = time
            else:
                time_column = time
                time_options = {}

            time = {
                'column': time_column,
                'method': 'count',
                'cumulative': False,
                'frames': 256,
                'duration': 30,
            }
            time.update(time_options)

        size = size or 10
        if isinstance(size, str):
            size = {'column': size}
        if isinstance(size, dict):
            if 'column' not in size:
                raise ValueError("size must include a 'column' value")
            if time:
                raise ValueError("When time is specified, size can"
                                 " only be a fixed size")
            old_size = size
            size = {
                'range'     : [5, 25],
                'bins'      : 10,
                'bin_method': BinMethod.quantiles,
            }
            size.update(old_size)
            # Since we're accessing min/max, convert range into a list
            size['range'] = list(size['range'])

        self.color   = color
        self.scheme  = scheme
        self.size    = size
        self.time    = time
        self.tooltip = tooltip
        self.legend  = legend


    def _setup(self, context, layers, layer_idx):
        basemap = layers[0]

        self.color = self.color or DEFAULT_COLORS[layer_idx]
        self.cartocss = self.get_cartocss(basemap)

        if self.time:
            column   = self.time['column']
            frames   = self.time['frames']
            method   = self.time['method']
            duration = self.time['duration']
            agg_func = "'{method}({time_column})'".format(method=method,
                                                          time_column=column)
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
            self.cartocss += self.torque_cartocss


    def get_cartocss(self, basemap):
        if isinstance(self.size, int):
            size_style = self.size
        elif isinstance(self.size, dict):
            size_style = ('ramp([{column}],'
                          ' range({min_range},{max_range}),'
                          ' {bin_method}({bins}))').format(column=self.size['column'],
                                                           min_range=self.size['range'][0],
                                                           max_range=self.size['range'][1],
                                                           bin_method=self.size['bin_method'],
                                                           bins=self.size['bins'])

        if self.scheme:
            color_style = get_scheme_cartocss(self.color, self.scheme)
        else:
            color_style = self.color

        line_color = '#000' if basemap.source == 'dark' else '#FFF'
        return cssify({
            # Point CSS
            "#layer['mapnik::geometry_type'=1]": {
                'marker-width': size_style,
                'marker-fill': color_style,
                'marker-fill-opacity': '1',
                'marker-allow-overlap': 'true',
                'marker-line-width': '0.5',
                'marker-line-color': line_color,
                'marker-line-opacity': '1',
            },
            # Line CSS
            "#layer['mapnik::geometry_type'=2]": {
                'line-width': '1.5',
                'line-color': color_style,
            },
            # Polygon CSS
            "#layer['mapnik::geometry_type'=3]": {
                'polygon-fill': color_style,
                'polygon-opacity': '0.9',
                'polygon-gamma': '0.5',
                'line-color': '#FFF',
                'line-width': '0.5',
                'line-opacity': '0.25',
                'line-comp-op': 'hard-light',
            }
        })


class Layer(QueryLayer):
    def __init__(self, table_name, source=None, overwrite=False, time=None, color=None, size=None,
                 tooltip=None, legend=None):

        self.table_name = table_name
        self.source     = source
        self.overwrite  = overwrite

        super(Layer, self).__init__('SELECT * FROM {}'.format(table_name),
                                    time=time,
                                    color=color,
                                    size=size,
                                    tooltip=tooltip,
                                    legend=legend)

    def _setup(self, context, layers, layer_idx):
        if isinstance(self.source, pd.DataFrame):
            context.write(self.source, self.table_name, overwrite=self.overwrite)
        super(Layer, self)._setup(context, layers, layer_idx)

# cdb_context.map([BaseMap('light'),
#                  BaseMap('dark'),
#                  BaseMap('https://{x}/{y}/{z}'),
#                  BaseMap('light', labels=[default: 'back', 'front', 'back', None]),
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
#                            'size': 'col2', # Option 2, by value Error if using time_column
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
#                                'col1': cartoframes.widgets.Histogram(use_global=True),
#                                'col2': cartoframes.widgets.Category(),
#                                'col3': cartoframes.widgets.Min(),
#                                'col4': cartoframes.widgets.Max(),
#                            },
#                        })
#                  QueryLayer('select * from foo',
#                             time_column='timestamp'),

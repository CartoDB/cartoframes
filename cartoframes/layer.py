import itertools
import pandas as pd
import random
import webcolors
from .utils import cssify
from .styling import BinMethod, mint, get_scheme_cartocss


DEFAULT_COLORS = ['#F9CA34', '#4ABD9A', '#4A5798', '#DF5E26',
                  '#F9CA34', '#4ABD9A', '#4A5798', '#DF5E26']


class AbstractLayer:
    is_basemap = False

    def __init__(self):
        pass

    def _setup(self, context, layers, layer_idx):
        pass


class BaseMap(AbstractLayer):
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
        else:
            # [BUG] Remove this once baselayer urls can be passed in named map config
            raise ValueError('BaseMap cannot contain a custom url at the moment')
            self.url = source

    def is_basic(self):
        return self.source in ('dark', 'light')


class QueryLayer(AbstractLayer):
    def __init__(self, query, time=None, color=None, size=None,
                 tooltip=None, legend=None):

        self.query = query

        color = color or None

        # If column was specified, force a scheme
        # It could be that there is a column named 'blue' for example
        if isinstance(color, dict):
            if 'column' not in color:
                raise ValueError("color must include a 'column' value")
            scheme = color.get('scheme', mint(5))
            color  = color['column']
        elif (color and
              color[0] != '#' and
              color not in webcolors.CSS3_NAMES_TO_HEX):
            color  = color
            scheme = mint(5)
        else:
            color  = color
            scheme = None

        if time:
            if isinstance(time, dict):
                if 'column' not in time:
                    raise ValueError("time must include a 'column' value")
                time_column  = time['column']
                time_options = time
            else:
                time_column  = time
                time_options = {}

            time = {
                'column'    : time_column,
                'method'    : 'count',
                'cumulative': False,
                'frames'    : 256,
                'duration'  : 30,
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
        self.cartocss = self.get_cartocss(basemap)

        self.color = self.color or DEFAULT_COLORS[layer_idx]

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

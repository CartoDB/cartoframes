"""legend generation functions
"""
try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
except ImportError:
    raise ImportError('Cannot create legends without `matplotlib` installed')
from cartoframes.styling import get_scheme
from carto.exceptions import CartoException
plt.style.use('ggplot')


def get_legend(sql, layer):
    pass


class Legend(object):
    def __init__(self, sql_client, layer, ax=None):
        self.edges = get_edges(sql_client, layer)
        self.legend = None
        self.layer = layer
        self.ax = ax

    def draw_legend(self):
        """Create a matplotlib legend"""
        # Make a figure and axes with dimensions as desired.
        if 'colors' in self.layer.scheme:
            cmap = mpl.colors.ListedColormap(self.layer.scheme['colors'])
        else:
            cmap = get_scheme(self.layer.scheme, 'mpl_colormap')
        fig = plt.figure(figsize=(8, 3))
        if self.ax is None:
            self.ax = fig.add_axes([0.05, 0.80, 0.9, 0.15])
        cmap.set_over('0.25')
        cmap.set_under('0.75')
        # length of bounds array must be one greater than length of color list
        norm = mpl.colors.BoundaryNorm(self.edges, cmap.N)
        cb = mpl.colorbar.ColorbarBase(
                self.ax,
                cmap=cmap,
                norm=norm,
                # to use 'extend', you must
                # specify two extra boundaries:
                boundaries=list(map(lambda x: round(x, 2), self.edges)),
                ticks=list(map(lambda x: round(x, 2), self.edges)),
                # ticks=list(map(lambda x: round(x, 2), self.edges)),
                spacing='proportional',
                orientation='horizontal')
        cb.set_label(self.layer.color)
        return cb


def get_edges(sql_client, layer):
    """Calculate bin edges for quantitative legend"""
    bin_method = bin_method_map(layer.scheme.get('bin_method', 'quantiles'))
    bin_query = ('min("{col}")::numeric || '
                 '{method}(array_agg("{col}"::numeric), '
                 '{n_bins})').format(method=bin_method,
                                     col=layer.color,
                                     n_bins=layer.scheme['bins'])
    try:
        bin_edges = sql_client.send('''
            SELECT {bin_query} AS bin_edges
              FROM ({query}) AS _wrap
              WHERE "{col}" is not null
               AND "{col}"::float != 'nan'
        '''.format(bin_query=bin_query,
                   query=layer.query,
                   col=layer.color))
        return bin_edges['rows'][0]['bin_edges']
    except CartoException as err:
        raise CartoException(err)


def bin_method_map(bin_method):
    """Given a `bin_method`, return the equivalent CARTO PostgreSQL bin
    function:
    https://github.com/CartoDB/cartodb-postgresql/tree/master/scripts-available

    Args:
        bin_method (str): Bin method. One of 'quantiles', 'equal', 'headtails',
          'jenks', or 'category'
    Returns:
        str: Equivalent function name from CARTO's PostgreSQL extension
    """
    func_mapping = {
        'equal': 'CDB_EqualIntervalBins',
        'quantiles': 'CDB_QuantileBins',
        'headtails': 'CDB_HeadsTailsBins',
        'jenks': 'CDB_JenksBins'
        }
    try:
        return func_mapping[bin_method]
    except KeyError:
        raise ValueError('Value `{val}` is not a valid option. Choose one of '
                         '{vals}'.format(val=bin_method,
                                         vals=', '.join(func_mapping.keys())))

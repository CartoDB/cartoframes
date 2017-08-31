"""legend generation functions
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from cartoframes.styling import get_scheme
from carto.exceptions import CartoException
plt.style.use('ggplot')

def draw_legend(edges, colname, scheme={'name': 'Blues', 'bins': 5}):
    """Create a matplotlib legend"""
    # Make a figure and axes with dimensions as desired.
    if 'colors' in scheme:
        cmap = mpl.colors.ListedColormap(scheme['colors'])
    else:
        cmap = get_scheme(scheme, 'mpl_colormap')
    fig = plt.figure(figsize=(8, 3))
    ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
    cmap.set_over('0.25')
    cmap.set_under('0.75')
    # length of bounds array must be one greater than length of color list
    bounds = edges
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                    norm=norm,
                                    # to use 'extend', you must
                                    # specify two extra boundaries:
                                    boundaries=list(map(lambda x: round(x, 2), bounds)),
                                    ticks=list(map(lambda x: round(x, 2), bounds)),
                                    # ticks=list(map(lambda x: round(x, 2), bounds)),
                                    spacing='proportional',
                                    orientation='horizontal')
    cb2.set_label(colname)
    plt.show(cb2)
    return fig

def get_legend(sql_client, layer):
    """Create a legend given the properties of `layer`
    """
    bin_query = 'min("{col}")::numeric || {method}(array_agg("{col}"::numeric), {n_bins})'.format(
        method=bin_method_map(layer.scheme.get('bin_method', 'quantiles')),
        col=layer.color,
        n_bins=layer.scheme['bins'])
    try:
        bin_edges = sql_client.send('''
            SELECT {bin_query} AS bin_edges
              FROM ({query}) AS _wrap
              WHERE "{col}" is not null
               AND "{col}"::float != 'nan'
        '''.format(
            bin_query=bin_query,
            query=layer.query,
            col=layer.color))
        edges = bin_edges['rows'][0]['bin_edges']
    except CartoException as err:
        raise CartoException(err)

    return draw_legend(edges, layer.color, layer.scheme)


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

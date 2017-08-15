import matplotlib as plt
import matplotlib as mpl
from carto.exceptions import CartoException


def draw_legend(edges, colname, scheme={'name': 'Blues', 'bins': 5}):
    """Create a matplotlib legend"""
    # Make a figure and axes with dimensions as desired.
    fig = plt.figure(figsize=(8, 3))
    ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])

    cmap = getattr(palettable.colorbrewer.sequential,
                   '{name}_{bins}'.format(**scheme)).mpl_colormap
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

def get_legend(sql_client, layer):
    """Create a legend given the properties of `layer`
    """

    func_mapping = {
	'equal': 'CDB_EqualIntervalBins',
	'quantiles': 'CDB_QuantileBins',
	'headtails': 'CDB_HeadsTailsBins',
	'jenks': 'CDB_JenksBins'
	}
    bin_query = 'min("{col}")::numeric || {method}(array_agg("{col}"::numeric), {n_bins})'.format(
        method=func_mapping(layer.scheme.get('bin_method', 'quantiles')),
        col=layer.color,
        n_bins=layer.scheme['bins'])
    print(bin_query)
    try:
        bin_edges = sql_client.send('''
            SELECT {bin_query} AS bin_edges
              FROM ({query}) AS _wrap
        '''.format(
            bin_query=bin_query,
            query=layer.query))
        edges = bin_edges['rows'][0]['bin_edges']
    except CartoException as err:
        raise CartoException(err)
    
    return draw_legend(edges)


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
        return func_mapping[bin_mapping]
    except KeyError:
        raise ValueError('Value `{val}` is not a valid option. Choose one of '
                         '{vals}'.format(val=bin_mapping,
                                         vals=', '.join(func_mapping.keys())))

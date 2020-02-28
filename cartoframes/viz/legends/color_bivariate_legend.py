from ..legend import Legend


def color_bivariate_legend(title=None, description=None, footer=None, prop='color',
                           variable=None, label_x='X', label_y='Y', bins=3, dynamic=False):
    """Helper function for quickly creating a color bivariate legend.

    Args:

    Returns:
        cartoframes.viz.legend.Legend

    Example:

    """

    options = {
      'labelX': label_x,
      'labelY': label_y,
      'numQuantiles': bins
    }

    return Legend('bivariate', title, description, footer, prop, variable, dynamic, options)

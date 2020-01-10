from ..legend import Legend


def basic_legend(title=None, description=None, footer=None):
    """Helper function for quickly creating a basic legend.

    Args:
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources

    Returns:
        cartoframes.viz.legend.Legend

    Example:
        >>> basic_legend(
        ...     title='Legend title',
        ...     description='Legend description',
        ...     footer='Legend footer')

    """

    return Legend('basic', title, description, footer)

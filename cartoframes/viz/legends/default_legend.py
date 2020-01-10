from ..legend import Legend


def default_legend(title=None, description=None, footer=None, **kwargs):
    """Helper function for quickly creating a default legend based on the style.
    A style helper is required.

    Args:
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources.

    Returns:
        cartoframes.viz.legend.Legend

    Example:
        >>> default_legend(
        ...     title='Legend title',
        ...     description='Legend description',
        ...     footer='Legend footer')

    """
    return Legend('default', title=title, description=description, footer=footer, **kwargs)

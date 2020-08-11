from ..widget import Widget


def formula_widget(value, operation=None, title=None, description=None, footer=None, format=None, is_global=False):
    """Helper function for quickly creating a formula widget.

    Formula widgets calculate aggregated values ('avg', 'max', 'min', 'sum') from numeric columns
    or counts of features ('count') in a dataset.

    A formula widget's aggregations can be calculated on 'global' or 'viewport' based values.
    If you want the values in a formula widget to update on zoom and/or pan, use viewport based aggregations.

    Args:
        value (str): Column name of the numeric value.
        operation (str): attribute for widget's aggregated value ('count', 'avg', 'max', 'min', 'sum').
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).
        is_global (boolean, optional): Account for calculations based on the entire dataset ('global') vs.
            the default of 'viewport' features.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> formula_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

        >>> formula_widget(
        ...     'column_name',
        ...     operation='sum',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer',
        ...     format='.2~s')

    """
    if isinstance(operation, str):
        operation = operation.lower()
    return Widget('formula', value, title, description, footer, operation=operation, format=format, is_global=is_global)

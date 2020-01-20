from . import color_category_style
from ...data.services.isolines import RANGE_LABEL_KEY


def isolines_style(value=RANGE_LABEL_KEY, top=11, cat=None, palette='pinkyl', size=None, opacity=0.8,
                   stroke_color='rgba(150,150,150,0.4)', stroke_width=None):
    """Helper function for quickly creating an isolines style.
    Based on the color category style.

    Args:
        value (str, optional): Column to symbolize by. Default is "range_label".
        top (int, optional): Number of categories. Default is 11. Values
            can range from 1 to 16.
        cat (list<str>, optional): Category list. Must be a valid list of categories.
        palette (str, optional): Palette that can be a named cartocolor palette
            or other valid color palette. Use `help(cartoframes.viz.palettes)` to
            get more information. Default is "pinkyl".
        size (int, optional): Size of point or line features.
        opacity (float, optional): Opacity value for point color and line features.
            Default is 0.8.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is 'rgba(150,150,150,0.4)'.
        stroke_width (int, optional): Size of the stroke on point features.

    Returns:
        cartoframes.viz.style.Style

    """
    return color_category_style(value, top, cat, palette, size, opacity, stroke_color, stroke_width)

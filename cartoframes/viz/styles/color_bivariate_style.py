from .utils import get_value
from ..style import Style
from ..legends import color_bivariate_legend
from ..popups import popup_element


def color_bivariate_style(first_value, second_value, method='quantiles', bins=3,
                          first_palette=None, second_palette=None, size=None,
                          opacity=None, stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color bivariate style.

    Args:

    Returns:
        cartoframes.viz.style.Style
    """

    if method not in ('quantiles', 'equal', 'stdev'):
        raise ValueError('Available methods are: "quantiles", "equal", "stdev".')

    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'
    first_palette = '[#e8e8e8, #dfb0d6, #be64ac]'
    second_palette = '[#e8e8e8, #ace4e4, #5ac8c8]'

    color = 'opacity(ramp(globalQuantiles(${0}, {2}), {3}) * ramp(globalQuantiles(${1}, {2}), {4}), {5})'.format(
      first_value,
      second_value,
      bins,
      first_palette,
      second_palette,
      get_value(opacity, 1)
    )

    data = {
        'point': {
            'color': color,
            'width': get_value(size, 'width', 'point'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': animation_filter
        },
        'polygon': {
            'color': color,
            'strokeColor': get_value(stroke_color, 'strokeColor', 'polygon'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'polygon'),
            'filter': animation_filter
        }
    }

    title = first_value + ' ' + second_value

    return Style(
        data,
        [first_value, second_value],
        default_legend=color_bivariate_legend(title=title),
        default_popup_hover=[
          popup_element(first_value, title=first_value),
          popup_element(second_value, title=second_value)
        ],
        default_popup_click=[
          popup_element(first_value, title=first_value),
          popup_element(second_value, title=second_value)
        ]
    )

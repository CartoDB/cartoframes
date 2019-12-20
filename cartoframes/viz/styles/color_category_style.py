from ..style import Style
from ..helpers.utils import serialize_palette, get_value


def color_category_style(
        value, top=11, cat=None, palette=None, size=None, opacity=None,
        stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color category style.

    Args:
        value (str): Column to symbolize by.
        top (int, optional): Number of categories. Default is 11. Values
          can range from 1 to 16.
        cat (list<str>, optional): Category list. Must be a valid list of categories.
        palette (str, optional): Palette that can be a named CARTOColor palette
          or other valid CARTO VL palette expression. Default is `bold`.
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        :py:class:`Style <cartoframes.viz.Style>`
    """
    func = 'buckets' if cat else 'top'
    default_palette = 'bold'
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    return Style({
          'point': {
              'color': 'opacity(ramp({0}(${1}, {2}), {3}),{4})'.format(
                  func, value, cat or top,
                  serialize_palette(palette) or default_palette,
                  get_value(opacity, 'point', 'opacity')
              ),
              'width': get_value(size, 'point', 'width'),
              'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
              'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
              'filter': animation_filter
          },
          'line': {
              'color': 'opacity(ramp({0}(${1}, {2}), {3}),{4})'.format(
                  func, value, cat or top,
                  serialize_palette(palette) or default_palette,
                  get_value(opacity, 'line', 'opacity')
              ),
              'width': get_value(size, 'line', 'width'),
              'filter': animation_filter
          },
          'polygon': {
              'color': 'opacity(ramp({0}(${1}, {2}), {3}), {4})'.format(
                  func, value, cat or top,
                  serialize_palette(palette) or default_palette,
                  get_value(opacity, 'polygon', 'opacity')
              ),
              'strokeColor': get_value(stroke_color, 'polygon', 'strokeColor'),
              'strokeWidth': get_value(stroke_width, 'polygon', 'strokeWidth'),
              'filter': animation_filter
          }
      })

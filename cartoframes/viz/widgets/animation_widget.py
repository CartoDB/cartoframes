from __future__ import absolute_import

from ..widget import Widget


def animation_widget(**kwargs):
    """Helper function for quickly creating an animated widget.

    The animation widget includes an animation status bar as well as controls to play or pause animated data.
    The `filter` property of your map's style, applied to either a date or numeric field, drives both
    the animation and the widget. Only **one** animation can be controlled per layer.
    To learn more about creating animations visit:
      - https://carto.com/developers/carto-vl/guides/animated-visualizations.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom

    Returns:
        cartoframes.viz.Widget: Widget with type='animation'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer
            from cartoframes.viz.widgets import animation_widget

            Map(
                Layer(
                    'seattle_collisions',
                    'filter: animation($incdate, 20, fade(0.5,0.5))',
                    widgets=[
                        animation_widget(
                            title='Collision Date',
                            description= 'Play, pause, or select the range of the animation'
                        )]
                )
            )
    """

    data = kwargs
    data['type'] = 'animation'
    return Widget(data)

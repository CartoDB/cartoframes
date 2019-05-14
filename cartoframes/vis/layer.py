from __future__ import absolute_import

from .source import Source
from .style import Style
from ..dataset import Dataset


class Layer(object):
    """Layer

    Args:
        source (str, :py:class:`Dataset <cartoframes.Dataset>`,
          :py:class:`Source <cartoframes.vis.Source>`): The source data.
        style (str, dict, :py:class:`Style <cartoframes.vis.Style>`,
          optional): The style of the visualization: `CARTO VL styling
          <https://carto.com/developers/carto-vl/guides/style-with-expressions/>`.
        interactivity (str, list, or dict, optional): This option adds
          interactivity (click or hover) to a layer to show popups.
          Defaults to ``hover`` if one of the following inputs are specified:
            - dict: If a :obj:`dict`, this must have the key `cols` with its
            value a list of columns. Optionally add `event` to choose ``hover``
            or ``click``. Specifying a `header` key/value pair adds a header to
            the popup that will be rendered in HTML.
        context (:py:class:`Context <cartoframes.Context>`):
          A Conext instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.vis.Source>` is pased as source,
          this context is simply ignored. If not provided the context will be
          automatically obtained from the default context.

    Example:

        .. code::

            from cartoframes import Context, set_default_context
            from cartoframes.vis import Layer

            context = Context(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )
            set_default_context(context)

            Layer(
                'SELECT * FROM populated_places WHERE adm0name = \'Spain\'',
                'color': 'red'
            )

        Setting the context.

        .. code::

            from cartoframes import Context
            from cartoframes.vis import Layer

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Layer(
                'SELECT * FROM populated_places WHERE adm0name = \'Spain\'',
                'color': 'red',
                context=context
            )
    """

    def __init__(self,
                 source,
                 style=None,
                 interactivity=None,
                 legend=None,
                 context=None):

        self.is_basemap = False
        self.source = _set_source(source, context)
        self.bounds = self.source.bounds
        self.orig_query = self.source.query
        self.style = _set_style(style)
        self.viz = _get_viz(self.style)
        self.interactivity = _parse_interactivity(interactivity)
        self.legend = legend


def _set_source(source, context):
    """Set a Source object from the input"""
    if isinstance(source, (str, Dataset)):
        return Source(source, context)
    elif isinstance(source, Source):
        return source
    else:
        raise ValueError('Wrong source')


def _set_style(style):
    """Set a Style object from the input"""
    if isinstance(style, (str, dict)):
        return Style(style)
    elif isinstance(style, Style):
        return style
    else:
        return Style()


def _get_viz(style):
    """Obtain the style vis object"""
    if style and style.viz:
        return style.viz
    else:
        return ''


def _parse_interactivity(interactivity):
    """Add interactivity syntax to the styling"""
    event_default = 'hover'

    if interactivity is None:
        return None
    elif isinstance(interactivity, dict):
        return {
            'event': interactivity.get('event', event_default),
            'header': interactivity.get('header'),
            'values': interactivity.get('values')
        }
    elif interactivity is True:
        return {
            'event': event_default,
        }
    else:
        raise ValueError('`interactivity` must be a dictionary')

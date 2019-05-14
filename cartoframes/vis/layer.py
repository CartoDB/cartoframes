from __future__ import absolute_import

from .source import Source
from .style import Style
from ..dataset import Dataset


class Layer(object):
    """CARTO VL layer

    Args:
        source (Source): The source data. It can be GeoJSON, SQL or Dataset.
        style (dict, tuple, list, optional): Style of the visualization. It
            can contain the following values:
        interactivity (str, list, or dict, optional): This option adds
            interactivity (click or hover) to a layer to show popups.
            Defaults to ``hover`` if one of the following inputs are specified:
                - dict: If a :obj:`dict`, this must have the key `cols` with its
                value a list of columns. Optionally add `event` to choose ``hover``
                or ``click``. Specifying a `header` key/value pair adds a header to
                the popup that will be rendered in HTML.

    Example:

        .. code::

            from cartoframes import carto_vl as vl
            from cartoframes import CartoContext

            context = CartoContext(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )

            vl.Map([
                vl.Layer(
                    source=vl.source.SQL('SELECT * FROM populated_places WHERE adm0name = \'Spain\''),
                    style=vl.Style({
                        'color': 'red'
                    })
                )],
                context=context
            )
    """

    def __init__(self,
                 source,
                 style=None,
                 interactivity=None,
                 legend=None):

        self.is_basemap = False
        self.source = _set_source(source)
        self.bounds = self.source.bounds
        self.orig_query = self.source.query
        self.style = _set_style(style)
        self.viz = _get_viz(self.style)
        self.interactivity = _parse_interactivity(interactivity)
        self.legend = legend


def _set_source(source):
    if isinstance(source, (str, Dataset)):
        return Source(source)
    elif isinstance(source, Source):
        return source
    else:
        raise ValueError('Wrong source')


def _set_style(style):
    if isinstance(style, (str, dict)):
        return Style(style)
    elif isinstance(style, Style):
        return style
    else:
        return Style()


def _parse_interactivity(interactivity):
    """Adds interactivity syntax to the styling"""
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


def _get_viz(style):
    if style and style.viz:
        return style.viz
    else:
        return ''

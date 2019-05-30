from __future__ import absolute_import

from .source import Source
from .style import Style
from .popup import Popup
from .legend import Legend
from ..dataset import Dataset


class Layer(object):
    """Layer

    Args:
        source (str, :py:class:`Dataset <cartoframes.Dataset>`,
          :py:class:`Source <cartoframes.viz.Source>`): The source data.
        style (str, dict, :py:class:`Style <cartoframes.viz.Style>`,
          optional): The style of the visualization: `CARTO VL styling
          <https://carto.com/developers/carto-vl/guides/style-with-expressions/>`.
        popup (dict, :py:class:`Popup <cartoframes.viz.Popup>`, optional):
          This option adds interactivity (click and hover) to a layer to show popups.
          The columns to be shown must be added in a list format for each event. It
          must be written using `CARTO VL expressions syntax
          <https://carto.com/developers/carto-vl/reference/#cartoexpressions>`.
        legend (dict, :py:class:`Legend <cartoframes.viz.Legend>`, optional):
          The legend definition for a layer. It contains the information
          to show a legend "type" (color-category, color-bins, color-continuous),
          "prop" (color) and also text information: "title", "description" and "footer".
        context (:py:class:`Context <cartoframes.Context>`):
          A Context instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.viz.Source>` is pased as source,
          this context is simply ignored. If not provided the context will be
          automatically obtained from the default context.

    Example:

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Layer

            set_default_context(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )

            Layer(
                'SELECT * FROM populated_places WHERE adm0name = \'Spain\'',
                'color: ramp(globalQuantiles($pop_max, 5), reverse(purpor))',
                popup={
                    'hover': '$name',
                    'click': ['$name', '$pop_max', '$pop_min']
                },
                legend={
                    'type': 'color-category',
                    'prop': 'color',
                    'title': 'Population'
                }
            )

        Setting the context.

        .. code::

            from cartoframes.auth import Context
            from cartoframes.viz import Layer

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Layer(
                'populated_places',
                'color: "red"',
                context=context
            )
    """

    def __init__(self,
                 source,
                 style=None,
                 popup=None,
                 legend=None,
                 context=None):

        self.is_basemap = False

        self.source = _set_source(source, context)
        self.style = _set_style(style)
        self.popup = _set_popup(popup)
        self.legend = _set_legend(legend)

        self.bounds = self.source.bounds
        self.orig_query = self.source.query
        self.viz = self.style.compute_viz(
            self.source.geom_type,
            self.popup.get_variables()
        )
        self.interactivity = self.popup.get_interactivity()
        self.legend_info = self.legend.get_info(
            self.source.geom_type
        )


def _set_source(source, context):
    """Set a Source class from the input"""
    if isinstance(source, (str, list, dict, Dataset)):
        return Source(source, context)
    elif isinstance(source, Source):
        return source
    else:
        raise ValueError('Wrong source')


def _set_style(style):
    """Set a Style class from the input"""
    if isinstance(style, (str, dict)):
        return Style(style)
    elif isinstance(style, Style):
        return style
    else:
        return Style()


def _set_popup(popup):
    """Set a Popup class from the input"""
    if isinstance(popup, dict):
        return Popup(popup)
    elif isinstance(popup, Popup):
        return popup
    else:
        return Popup()


def _set_legend(legend):
    """Set a Legend class from the input"""
    if isinstance(legend, dict):
        return Legend(legend)
    elif isinstance(legend, Legend):
        return legend
    else:
        return Legend()

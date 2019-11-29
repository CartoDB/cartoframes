from __future__ import absolute_import

import pandas

from ..utils.utils import merge_dicts
from .legend import Legend
from .legend_list import LegendList
from .popup import Popup
from .source import Source
from .style import Style
from .widget_list import WidgetList

from ..utils.utils import extract_viz_columns


class Layer(object):
    """Layer to display data on a map. This class can be used as one or more
    layers in :py:class:`Map <cartoframes.viz.Map>` or on its own in a Jupyter
    notebook to get a preview of a Layer.

    Args:
        source (str, :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`,
            pandas.DataFrame, geopandas.GeoDataFrame): The source data.
        style (str, dict, or :py:class:`Style <cartoframes.viz.Style>`, optional):
            The style of the visualization.
        popup (dict or :py:class:`Popup <cartoframes.viz.Popup>`, optional):
            This option adds interactivity (click and hover) to a layer to show popups.
            The columns to be shown must be added in a list format for each event.
            See :py:class:`Popup <cartoframes.viz.Popup>` for more information.
        legend (dict or :py:class:`Legend <cartoframes.viz.Legend>`, optional):
            The legend definition for a layer. It contains the information
            to show a legend "type" (``color-category``, ``color-bins``,
            ``color-continuous``), "prop" (color) and also text information:
            "title", "description" and "footer". See :py:class:`Legend
            <cartoframes.viz.Legend>` for more information.
        widgets (dict, list, or :py:class:`WidgetList <cartoframes.viz.WidgetList>`, optional):
            Widget or list of widgets for a layer. It contains the information to display
            different widget types on the top right of the map. See
            :py:class:`WidgetList` for more information.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. This is only used for the simplified Source API.
            When a :py:class:`Source <cartoframes.viz.Source>` is pased as source,
            these credentials is simply ignored. If not provided the credentials will be
            automatically obtained from the default credentials.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
          keys, or an array of floats in the following structure: [[west,
          south], [east, north]]. If not provided the bounds will be automatically
          calculated to fit all features.
        geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.


    Example:

        Create a layer with a custom popup, legend, and widget.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Layer

            set_default_credentials(
                base_url='https://cartovl.carto.com',
                api_key='default_public'
            )

            Layer(
                "SELECT * FROM populated_places WHERE adm0name = 'Spain'",
                'color: ramp(globalQuantiles($pop_max, 5), reverse(purpor))',
                popup={
                    'hover': '$name',
                    'click': ['$name', '$pop_max', '$pop_min']
                },
                legend={
                    'type': 'color-category',
                    'title': 'Population'
                },
                widgets=[{
                    'type': 'formula',
                    'title': 'Avg $pop_max',
                    'value': 'viewportAvg($pop_max)'
                }]
            )

        Create a layer specifically tied to a :py:class:`Credentials
        <cartoframes.auth.Credentials>` and display it on a map.

        .. code::

            from cartoframes.auth import Credentials
            from cartoframes.viz import Layer, Map

            credentials = Credentials(
                base_url='https://cartovl.carto.com',
                api_key='default_public'
            )

            pop_layer = Layer(
                'populated_places',
                'color: red',
                credentials=credentials
            )
            Map(pop_layer)

        Preview a layer in a Jupyter notebook. Note: if in a Jupyter notebook,
        it is not required to explicitly add a Layer to a :py:class:`Map
        <cartoframes.viz.Map>` if only visualizing data as a single layer.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Layer, Map

            set_default_credentials('https://cartoframes.carto.com')

            pop_layer = Layer(
                'brooklyn_poverty',
                'color: ramp($poverty_per_pop, sunset)',
                legend={
                    'type': 'color-continuous',
                    'title': 'Poverty per pop'
                }
            )
            pop_layer
    """

    def __init__(self,
                 source,
                 style=None,
                 popup=None,
                 legend=None,
                 widgets=None,
                 credentials=None,
                 bounds=None,
                 geom_col=None):

        self.is_basemap = False

        self.source = _set_source(source, credentials, geom_col)
        self.style = _set_style(style)
        self.popup = _set_popup(popup)
        self.legend = _set_legend(legend)
        self.widgets = _set_widgets(widgets)

        geom_type = self.source.get_geom_type()
        popup_variables = self.popup.get_variables()
        widget_variables = self.widgets.get_variables()
        external_variables = merge_dicts(popup_variables, widget_variables)
        self.viz = self.style.compute_viz(geom_type, external_variables)
        viz_columns = extract_viz_columns(self.viz)

        self.source.compute_metadata(viz_columns)
        self.source_type = self.source.type
        self.source_data = self.source.data
        self.bounds = bounds or self.source.bounds
        self.credentials = self.source.get_credentials()
        self.interactivity = self.popup.get_interactivity()
        self.widgets_info = self.widgets.get_widgets_info()
        self.legend_info = self.legend.get_info(geom_type) if self.legend is not None else None
        self.has_legend_list = isinstance(self.legend, LegendList)

    def _repr_html_(self):
        from .map import Map
        return Map(self)._repr_html_()


def _set_source(source, credentials, geom_col):
    """Set a Source class from the input"""
    if isinstance(source, (str, pandas.DataFrame)):
        return Source(source, credentials, geom_col)
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
    if isinstance(legend, (Legend, LegendList)):
        return legend
    if isinstance(legend, dict):
        return Legend(legend)
    if isinstance(legend, (list)):
        return LegendList(legend)
    else:
        return Legend('')


def _set_widgets(widgets):
    if isinstance(widgets, (dict, list)):
        return WidgetList(widgets)
    if isinstance(widgets, WidgetList):
        return widgets
    else:
        return WidgetList()

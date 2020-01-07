import pandas

from ..utils.utils import merge_dicts
from .legend import Legend
from .legend_list import LegendList
from .popup import Popup
from .popup_list import PopupList
from .source import Source
from .style import Style
from .widget import Widget
from .widget_list import WidgetList

from ..utils.utils import extract_viz_columns


class Layer:
    """Layer to display data on a map. This class can be used as one or more
    layers in :py:class:`Map <cartoframes.viz.Map>` or on its own in a Jupyter
    notebook to get a preview of a Layer.

    Note: in a Jupyter notebook, it is not required to explicitly add a Layer to a
        :py:class:`Map <cartoframes.viz.Map>` if only visualizing data as a single layer.

    Args:
        source (str, pandas.DataFrame, geopandas.GeoDataFrame,
            :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`): The source data:
            table name, SQL query or a dataframe.
        style (dict, or :py:class:`Style <cartoframes.viz.Style>`, optional):
            The style of the visualization.
        legends (bool, :py:class:`Legend <cartoframes.viz.Legend>` list, optional):
            The legends definition for a layer. It contains a list of legend helpers.
            See :py:class:`Legend <cartoframes.viz.Legend>` for more information.
        widgets (bool, list, or :py:class:`WidgetList <cartoframes.viz.WidgetList>`, optional):
            Widget or list of widgets for a layer. It contains the information to display
            different widget types on the top right of the map. See
            :py:class:`WidgetList` for more information.
        click_popup(`popup_element <cartoframes.viz.popup_element>` list, optional):
            Set up a popup to be displayed on a click event.
        hover_popup(bool, `popup_element <cartoframes.viz.popup_element>` list, optional):
            Set up a popup to be displayed on a hover event. Style helpers include a default hover popup,
            set it to `hover_popup=False` to remove it.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. This is only used for the simplified Source API.
            When a :py:class:`Source <cartoframes.viz.Source>` is passed as source,
            these credentials is simply ignored. If not provided the credentials will be
            automatically obtained from the default credentials.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
            keys, or an array of floats in the following structure: [[west,
            south], [east, north]]. If not provided the bounds will be automatically
            calculated to fit all features.
        geom_col (str, optional): string indicating the geometry column name in the source `DataFrame`.

    Example:

        Create a layer with the defaults (style, legend).

        >>> Layer('table_name')  # or Layer(gdf)

        Create a layer with a custom style, legend, widget and popups.

        >>> Layer(
        ...     'table_name',
        ...     style=color_bins_style('column_name'),
        ...     legends=color_bins_legend(title='Legend title'),
        ...     widgets=histogram_widget('column_name', title='Widget title'),
        ...     click_popup=popup_element('column_name', title='Popup title')
        ...     hover_popup=popup_element('column_name', title='Popup title')
        >>> )

        Create a layer specifically tied to a :py:class:`Credentials
        <cartoframes.auth.Credentials>`.

        >>> Layer(
        ...     'table_name',
        ...     credentials=Credentials.from_file('creds.json')
        >>> )

    """
    def __init__(self,
                 source,
                 style=None,
                 legends=True,
                 widgets=False,
                 click_popup=False,
                 hover_popup=True,
                 credentials=None,
                 bounds=None,
                 geom_col=None):

        self.is_basemap = False
        self.source = _set_source(source, credentials, geom_col)
        self.style = _set_style(style)

        self.popups = self._init_popups(click_popup, hover_popup)
        self.legends = self._init_legends(legends)
        self.widgets = self._init_widgets(widgets)

        geom_type = self.source.get_geom_type()
        popups_variables = self.popups.get_variables()
        widget_variables = self.widgets.get_variables()
        external_variables = merge_dicts(popups_variables, widget_variables)
        self.viz = self.style.compute_viz(geom_type, external_variables)
        viz_columns = extract_viz_columns(self.viz)

        self.source.compute_metadata(viz_columns)
        self.source_type = self.source.type
        self.source_data = self.source.data
        self.bounds = bounds or self.source.bounds
        self.credentials = self.source.get_credentials()
        self.interactivity = self.popups.get_interactivity()
        self.widgets_info = self.widgets.get_widgets_info()
        self.legends_info = self.legends.get_info() if self.legends is not None else None
        date_column_names = self.source.get_date_column_names()
        self.options = _set_options(date_column_names)
        self.has_legend_list = isinstance(self.legends, LegendList)

    def _init_legends(self, legends):
        if legends is True:
            return _set_legends(self.style.default_legends)
        if legends:
            return _set_legends(legends)
        return LegendList()

    def _init_widgets(self, widgets):
        if widgets is True:
            return _set_widgets(self.style.default_widgets)
        if widgets:
            return _set_widgets(widgets)
        return WidgetList()

    def _init_popups(self, click_popup, hover_popup):
        popups = {}
        if click_popup is True and self.style.default_popups is not None:
            click_popup = self.style.default_popups.get('click')
        if hover_popup is True and self.style.default_popups is not None:
            hover_popup = self.style.default_popups.get('hover')
        if click_popup:
            popups['click'] = click_popup
        if hover_popup:
            popups['hover'] = hover_popup
        return _set_popups(popups)

    def _repr_html_(self):
        from .map import Map
        return Map(self)._repr_html_()


def _set_source(source, credentials, geom_col):
    if isinstance(source, (str, pandas.DataFrame)):
        return Source(source, credentials, geom_col)
    elif isinstance(source, Source):
        return source
    else:
        raise ValueError('Wrong source')


def _set_style(style):
    if isinstance(style, str):
        # Only for testing purposes
        return Style(data=style)
    if isinstance(style, dict):
        return Style(style)
    elif isinstance(style, Style):
        return style
    else:
        return Style()


def _set_legends(legends):
    if isinstance(legends, Legend):
        return LegendList(legends)
    if isinstance(legends, LegendList):
        return legends
    if isinstance(legends, list):
        return LegendList(legends)
    else:
        return LegendList()


def _set_widgets(widgets):
    if isinstance(widgets, Widget):
        return WidgetList(widgets)
    if isinstance(widgets, list):
        return WidgetList(widgets)
    if isinstance(widgets, WidgetList):
        return widgets
    else:
        return WidgetList()


def _set_popups(popups):
    if isinstance(popups, (dict, Popup)):
        return PopupList(popups)
    else:
        return PopupList()


def _set_options(date_column_names):
    if isinstance(date_column_names, list):
        return {'dateColumns': date_column_names}

    return {}

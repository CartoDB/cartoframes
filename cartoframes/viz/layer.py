import pandas

from .legend import Legend
from .legend_list import LegendList
from .popup import Popup
from .popup_list import PopupList
from .source import Source
from .style import Style
from .widget import Widget
from .widget_list import WidgetList

from ..utils.utils import merge_dicts, extract_viz_columns


class Layer:
    """Layer to display data on a map. This class can be used as one or more
    layers in :py:class:`Map <cartoframes.viz.Map>` or on its own in a Jupyter
    notebook to get a preview of a Layer.

    Note: in a Jupyter notebook, it is not required to explicitly add a Layer to a
        :py:class:`Map <cartoframes.viz.Map>` if only visualizing data as a single layer.

    Args:
        source (str, pandas.DataFrame, geopandas.GeoDataFrame): The source data:
            table name, SQL query or a dataframe. If dataframe, the geometry's CRS must be WGS 84 (EPSG:4326).
        style (dict, or :py:class:`Style <cartoframes.viz.style.Style>`, optional):
            The style of the visualization.
        legends (bool, :py:class:`Legend <cartoframes.viz.legend.Legend>` list, optional):
            The legends definition for a layer. It contains a list of legend helpers.
            See :py:class:`Legend <cartoframes.viz.legend.Legend>` for more information.
        widgets (bool, list, or :py:class:`WidgetList <cartoframes.viz.widget_list.WidgetList>`, optional):
            Widget or list of widgets for a layer. It contains the information to display
            different widget types on the top right of the map. See
            :py:class:`WidgetList` for more information.
        popup_click(`popup_element <cartoframes.viz.popup_element>` list, optional):
            Set up a popup to be displayed on a click event.
        popup_hover(bool, `popup_element <cartoframes.viz.popup_element>` list, optional):
            Set up a popup to be displayed on a hover event. Style helpers include a default hover popup,
            set it to `popup_hover=False` to remove it.
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
        default_legend (bool, optional): flag to set the default legend. This only works when using a
            style helper. Default True.
        default_widget (bool, optional): flag to set the default widget. This only works when using a
            style helper. Default False.
        default_popup_hover (bool, optional): flag to set the default popup hover. This only works when using a
            style helper. Default True.
        default_popup_click (bool, optional): flag to set the default popup click. This only works when using a
            style helper. Default False.
        title (str, optional): title for the default legend, widget and popups.
        encode_data (bool, optional): By default, local data is encoded in order to save local space.
            However, when using very large files, it might not be possible to encode all the data.
            By disabling this parameter with `encode_data=False` the resulting notebook will be large,
            but there will be no encoding issues.


    Raises:
        ValueError: if the source is not valid.


    Examples:
        Create a layer with the defaults (style, legend).

        >>> Layer('table_name')  # or Layer(gdf)

        Create a layer with a custom style, legend, widget and popups.

        >>> Layer(
        ...     'table_name',
        ...     style=color_bins_style('column_name'),
        ...     legends=color_bins_legend(title='Legend title'),
        ...     widgets=histogram_widget('column_name', title='Widget title'),
        ...     popup_click=popup_element('column_name', title='Popup title')
        ...     popup_hover=popup_element('column_name', title='Popup title'))

        Create a layer specifically tied to a :py:class:`Credentials
        <cartoframes.auth.Credentials>`.

        >>> Layer(
        ...     'table_name',
        ...     credentials=Credentials.from_file('creds.json'))

    """
    def __init__(self,
                 source,
                 style=None,
                 legends=None,
                 widgets=None,
                 popup_hover=None,
                 popup_click=None,
                 credentials=None,
                 bounds=None,
                 geom_col=None,
                 default_legend=True,
                 default_widget=False,
                 default_popup_hover=True,
                 default_popup_click=False,
                 title=None,
                 parent_map=None,
                 encode_data=True):

        self.is_basemap = False
        self.default_legend = default_legend
        self.source = _set_source(source, credentials, geom_col, encode_data)
        self.style = _set_style(style)
        self.encode_data = encode_data
        self.parent_map = None
        self.geom_type = self.source.get_geom_type()
        self.popups = self._init_popups(
            popup_hover, popup_click, default_popup_hover, default_popup_click, title)
        self.legends = self._init_legends(legends, default_legend, title)
        self.widgets = self._init_widgets(widgets, default_widget, title)
        self.title = title
        popups_variables = self.popups.get_variables()
        widget_variables = self.widgets.get_variables()
        external_variables = merge_dicts(popups_variables, widget_variables)
        self._map_index = 0

        self.viz = self.style.compute_viz(self.geom_type, external_variables)
        viz_columns = extract_viz_columns(self.viz)

        self.source.compute_metadata(viz_columns)
        self.source_type = self.source.type
        self.source_data = self.source.data
        self.bounds = bounds or self.source.bounds
        self.credentials = self.source.get_credentials()
        self.interactivity = self.popups.get_interactivity()
        self.widgets_info = self.widgets.get_widgets_info()
        self.legends_info = self.legends.get_info() if self.legends is not None else None
        self.options = self._set_options()
        self.has_legend_list = isinstance(self.legends, LegendList)

    def _init_legends(self, legends, default_legend, title):
        if legends:
            return _set_legends(legends, self.style.default_legend, self.geom_type)

        if default_legend is True:
            default_legend = self.style.default_legend
            if default_legend is not None:
                default_legend.set_title(title)
            return _set_legends(default_legend, geom_type=self.geom_type)

        return LegendList()

    def _init_widgets(self, widgets, default_widget, title):
        if widgets:
            return _set_widgets(widgets, self.style.default_widget)

        if default_widget is True:
            default_widget = self.style.default_widget
            if default_widget is not None:
                default_widget.set_title(title)
            return _set_widgets(default_widget)

        return WidgetList()

    def _init_popups(self, popup_hover, popup_click, default_popup_hover, default_popup_click, title):
        popups = {}

        if popup_hover:
            popups['hover'] = popup_hover
        elif default_popup_hover is True and self.style.default_popup_hover is not None:
            popups['hover'] = self.style.default_popup_hover
            popups['hover']['title'] = title

        if popup_click:
            popups['click'] = popup_click
        elif default_popup_click is True and self.style.default_popup_click is not None:
            popups['click'] = self.style.default_popup_click
            popups['click']['title'] = title

        return _set_popups(popups, self.style.default_popup_hover, self.style.default_popup_click)

    def _set_options(self):
        date_column_names = self.source.get_datetime_column_names()

        if isinstance(date_column_names, list):
            return {'dateColumns': date_column_names}

        return {}

    def get_layer_def(self):
        return {
            'credentials': self.credentials,
            'interactivity': self.interactivity,
            'legends': self.legends_info,
            'has_legend_list': self.has_legend_list,
            'encode_data': self.encode_data,
            'widgets': self.widgets_info,
            'data': self.source_data,
            'type': self.source_type,
            'title': self.title,
            'options': self.options,
            'map_index': self.map_index,
            'source': self.source_data,
            'viz': self.viz
        }

    def _repr_html_(self):
        from .map import Map
        return Map(self)._repr_html_()

    @property
    def map_index(self):
        """Layer map index"""
        return self._map_index

    @map_index.setter
    def map_index(self, map_index):
        """Set session"""
        self._map_index = map_index

    def reset_ui(self, parent_map):
        if parent_map.is_static:
            # Remove legends/widgets if the map is static
            self.legends = []
            self.widgets = []
            self.legends_info = []
            self.widgets_info = []
        elif parent_map.layer_selector:
            if self.style.default_legend:
                self.style.default_legend.set_title('')
            self.legends = self._init_legends(self.legends, self.default_legend, '')
            self.legends_info = self.legends.get_info() if self.legends is not None else None


def _set_source(source, credentials, geom_col, encode_data):
    if isinstance(source, (str, pandas.DataFrame)):
        return Source(source, credentials, geom_col, encode_data)
    elif isinstance(source, Source):
        return source
    else:
        raise ValueError('Wrong source. Valid sources are string, DataFrame or GeoDataFrame.')


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


def _set_legends(legends, default_legend=None, geom_type=None):
    if isinstance(legends, list):
        return LegendList(legends, default_legend, geom_type)
    if isinstance(legends, Legend):
        return LegendList([legends], default_legend, geom_type)
    if isinstance(legends, LegendList):
        return legends
    else:
        return LegendList(geom_type=geom_type)


def _set_widgets(widgets, default_widget=None):
    if isinstance(widgets, list):
        return WidgetList(widgets, default_widget)
    if isinstance(widgets, Widget):
        return WidgetList([widgets], default_widget)
    if isinstance(widgets, WidgetList):
        return widgets
    else:
        return WidgetList()


def _set_popups(popups, default_popup_hover=None, default_popup_click=None):
    if isinstance(popups, (dict, Popup)):
        return PopupList(popups, default_popup_hover, default_popup_click)
    else:
        return PopupList()

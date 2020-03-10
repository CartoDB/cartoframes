from .widget import Widget
from .styles.utils import prop


class WidgetList:
    """WidgetList

    Args:
        widgets (list, Widget): The list of widgets for a layer.

    """
    def __init__(self, widgets=None, default_widget=None):
        self._widgets = self._init_widgets(widgets, default_widget)

    def _init_widgets(self, widgets, default_widget):
        if isinstance(widgets, list):
            widget_list = []
            for widget in widgets:
                if isinstance(widget, dict):
                    widget_list.append(Widget(widget))
                elif isinstance(widget, Widget):
                    if widget._type == 'default' and default_widget:
                        widget._type = default_widget._type
                        widget._prop = default_widget._prop
                        widget._value = default_widget._value
                    widget_list.append(widget)
            return widget_list
        if isinstance(widgets, dict):
            return [Widget(widgets)]
        else:
            return []

    def get_widgets_info(self):
        widgets_info = []
        for widget in self._widgets:
            if widget:
                widgets_info.append(widget.get_info())

        return widgets_info

    def get_variables(self):
        output = {}
        for widget in self._widgets:
            if widget._variable_name:
                output[widget._variable_name] = prop(widget._value) if widget.has_bridge() else widget._value

        return output

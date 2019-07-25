from __future__ import absolute_import

from .widget import Widget


class WidgetList(object):
    """WidgetList
     Args:
        widgets (dict, list, Widget): The list of widgets for a layer.

    Example:

        .. code::python

            from cartoframes.viz import Widget

            WidgetList([{
                type: 'formula',
                value: 'viewportSum($amount)'
                title: '...',
                description: '...',
                footer: '...'
            }, {
                'type': 'default',
                'value': '"Custom Info"',
            }])
    """

    def __init__(self, widgets=None):
        self._widgets = self._init_widgets(widgets)

    def _init_widgets(self, widgets):
        if isinstance(widgets, list):
            widget_list = []
            for widget in widgets:
                if isinstance(widget, dict):
                    widget_list.append(Widget(widget))
                elif isinstance(widget, Widget):
                    widget_list.append(widget)
            return widget_list
        if isinstance(widgets, dict):
            return [Widget(widgets)]
        elif isinstance(widgets, Widget):
            return [widgets]
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
                output[widget._variable_name] = '$' + widget._value if widget.has_bridge() else widget._value

        return output

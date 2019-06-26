from __future__ import absolute_import

from .widget import Widget


class WidgetList(object):
    def __init__(self, widgets=None):
        self.widgets = self._initwidgets(widgets)

    def _initwidgets(self, widgets):
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

    def get_variables(self):
        variables = {}
        for widget in self.widgets:
            if widget and widget._type != 'default':
                variables[widget._name] = widget._value
        return variables

    def getwidgets_info(self):
        widgets_info = []
        for widget in self.widgets:
            if widget:
                widgets_info.append(widget.get_info())

        return widgets_info

from ..utils.utils import merge_dicts, text_match
from . import defaults

from .popups import popup_element
from .widgets import basic_widget
from .widgets import category_widget
from .widgets import histogram_widget
from .widgets import time_series_widget

from .legend_list import LegendList
from .legends import basic_legend
from .legends import color_bins_legend
from .legends import color_category_legend
from .legends import color_continuous_legend
from .legends import size_bins_legend
from .legends import size_category_legend
from .legends import size_continuous_legend


class Style():
    """Style

    Args:
        data (str, dict): The style for the layer.
    """

    def __init__(self, style_type='default', value=None, data=None, popups=None, animate=None):
        self._style_type = style_type
        self._value = value
        self._popups = popups
        self._style = self._init_style(data=data)

    def _init_style(self, data):
        if data is None:
            return defaults.STYLE
        elif isinstance(data, (str, dict)):
            return data
        else:
            raise ValueError('`style` must be a dictionary')

    @property
    def value(self):
        return self._value

    def default_popups(self):
        return self._get_default_popups()

    def default_legends(self):
        if self._value is None:
            return LegendList()

        return LegendList(self._get_default_legends())

    def default_widgets(self):
        return self._get_default_widgets()

    def compute_viz(self, geom_type, variables={}):
        style = self._style
        default_style = defaults.STYLE[geom_type]

        if isinstance(style, dict):
            if geom_type in style:
                style = style.get(geom_type)
            return self._parse_style_dict(style, default_style, variables)
        else:
            raise ValueError('`style` must be a dictionary')

    def _get_default_popups(self):
        if self._value:
            return self._popups if self._popups else {'hover': [popup_element(self._value, self._value)]}

        return None

    def _get_default_legends(self):
        title = self._value

        if self._style_type == 'default':
            return basic_legend(title)

        if self._style_type == 'animation':
            return None

        if self._style_type == 'color-bins':
            return color_bins_legend(title)

        if self._style_type == 'color-category':
            return color_category_legend(title)

        if self._style_type == 'color-continuous':
            return color_continuous_legend(title)

        if self._style_type == 'size-bins':
            return size_bins_legend(title)

        if self._style_type == 'size-category':
            return size_category_legend(title)

        if self._style_type == 'size-continuous':
            return size_continuous_legend(title)

        if self._style_type == 'cluster-size':
            return size_continuous_legend(title)

        if self._style_type == 'isolines':
            return color_category_legend(title)

    def _get_default_widgets(self):
        title = self._value

        if self._style_type == 'default':
            return basic_widget(title)

        if self._style_type == 'animation':
            return time_series_widget(self._value, title)

        if self._style_type == 'color-bins':
            title = title or 'Distribution'
            return histogram_widget(self._value, title)

        if self._style_type == 'color-category':
            return category_widget(self._value, title)

        if self._style_type == 'color-continuous':
            return histogram_widget(self._value, title)

        if self._style_type == 'size-bins':
            return histogram_widget(self._value, title)

        if self._style_type == 'size-category':
            return category_widget(self._value, title)

        if self._style_type == 'size-continuous':
            return histogram_widget(self._value, title)

        if self._style_type == 'cluster-size':
            title = title or 'Distribution'
            return histogram_widget(self._value, title)

        if self._style_type == 'isolines':
            return None

    def _parse_style_dict(self, style, default_style, ext_vars):
        variables = merge_dicts(style.get('vars', {}), ext_vars)
        properties = merge_dicts(default_style, style)

        serialized_variables = self._serialize_variables(variables)
        serialized_properties = self._serialize_properties(properties)

        return serialized_variables + serialized_properties

    def _parse_style_str(self, style, default_style, ext_vars):
        variables = ext_vars
        default_properties = self._prune_defaults(default_style, style)

        serialized_variables = self._serialize_variables(variables)
        serialized_default_properties = self._serialize_properties(default_properties)

        return serialized_variables + serialized_default_properties + style

    def _serialize_variables(self, variables={}):
        output = ''
        for var in variables:
            output += '@{name}: {value}\n'.format(
                name=var,
                value=variables.get(var)
            )
        return output

    def _serialize_properties(self, properties={}):
        output = ''
        for prop in properties:
            if prop == 'vars':
                continue
            output += '{name}: {value}\n'.format(
                name=prop,
                value=properties.get(prop)
            )
        return output

    def _prune_defaults(self, default_style, style):
        output = default_style.copy()
        if 'color' in output and text_match(r'color\s*:', style):
            del output['color']
        if 'width' in output and text_match(r'width\s*:', style):
            del output['width']
        if 'strokeColor' in output and text_match(r'strokeColor\s*:', style):
            del output['strokeColor']
        if 'strokeWidth' in output and text_match(r'strokeWidth\s*:', style):
            del output['strokeWidth']
        return output

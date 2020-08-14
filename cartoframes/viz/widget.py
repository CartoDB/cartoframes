from . import constants
from ..utils.utils import camel_dictionary


class Widget:
    """Widgets are added to each layer and displayed in the visualization

    Available widgets are:
        - :py:meth:`basic_widget <cartoframes.viz.basic_widget>`
        - :py:meth:`formula_widget <cartoframes.viz.formula_widget>`
        - :py:meth:`category_widget <cartoframes.viz.category_widget>`
        - :py:meth:`histogram_widget <cartoframes.viz.histogram_widget>`
        - :py:meth:`time_series_widget <cartoframes.viz.time_series_widget>`
        - :py:meth:`animation_widget <cartoframes.viz.animation_widget>`

    """
    def __init__(self, widget_type, value=None, title=None, description=None, footer=None, prop=None, read_only=False,
                 buckets=20, weight=1, operation=None, format=None, is_global=False):
        self._check_type(widget_type)

        self._type = widget_type
        self._value = value
        self._title = title
        self._description = description
        self._footer = footer
        self._prop = self._get_prop(prop)
        self._read_only = read_only
        self._buckets = buckets
        self._weight = weight
        self._operation = operation
        self._format = format
        self._is_global = is_global
        self._options = self._build_options()

    def set_title(self, title):
        if title is not None:
            self._title = title

    def get_info(self):
        if self._type or self._title or self._description or self._footer:
            return {
                'type': self._type,
                'prop': self._prop,
                'value': self._value,
                'operation': self._operation,
                'title': self._title or '',
                'description': self._description,
                'footer': self._footer or '',
                'has_bridge': self.has_bridge(),
                'is_global': self._is_global,
                'options': self._options
            }

        else:
            return {}

    def _get_prop(self, prop):
        if not prop:
            return ''
        return constants.VIZ_PROPERTIES_MAP.get(prop)

    def has_bridge(self):
        return self._type not in ('formula', 'basic')  # TODO: We should remove 'formula' from here

    def _check_type(self, widget_type):
        if widget_type and widget_type not in constants.WIDGET_TYPES:
            raise ValueError(
                'Widget type is not valid. Valid widget types are: {}.'.format(
                    ', '.join(constants.WIDGET_TYPES)
                ))

    def _build_options(self):
        options = {
            'read_only': self._read_only,
            'buckets': self._buckets,
            'weight': self._weight,
            'format': self._format,
            'autoplay': True
            # TODO: `autoplay: False` is not working on Airship,
            # so it should be fixed when autoplay param is exposed in CF API
        }

        return camel_dictionary(options)

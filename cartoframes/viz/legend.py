from . import constants


class Legend:
    """Legends are added to each layer and displayed in the visualization

    Available legends are:
        - :py:meth:`basic_legend <cartoframes.viz.basic_legend>`
        - :py:meth:`color_bins_legend <cartoframes.viz.color_bins_legend>`
        - :py:meth:`color_category_legend <cartoframes.viz.color_category_legend>`
        - :py:meth:`color_continuous_legend <cartoframes.viz.color_continuous_legend>`
        - :py:meth:`size_bins_legend <cartoframes.viz.size_bins_legend>`
        - :py:meth:`size_category_legend <cartoframes.viz.size_category_legend>`
        - :py:meth:`size_continuous_legend <cartoframes.viz.size_continuous_legend>`

    """
    def __init__(self, legend_type=None, title=None, description=None,
                 footer=None, prop=None, variable='', dynamic=True,
                 ascending=False, format=None):
        self._check_type(legend_type)
        self._check_prop(prop)
        self._type = legend_type
        self._title = title
        self._description = description
        self._footer = footer
        self._prop = prop
        self._variable = variable
        self._dynamic = dynamic
        self._ascending = ascending
        self._format = format

    def add_defaults(self, title=None):
        self._title = self._title or title

    def set_title(self, title):
        if title is not None:
            self._title = title

    def get_info(self):
        if self._type or self._title or self._description or self._footer:
            _prop = self._get_prop(self._type)

            return {
                'type': self._type,
                'prop': _prop,
                'variable': self._variable,
                'dynamic': self._dynamic,
                'ascending': self._ascending,
                'title': self._title or '',
                'description': self._description or '',
                'footer': self._footer or '',
                'format': self._format
            }
        else:
            return {}

    def _get_prop(self, _type):
        if _type and not self._prop:
            _prop = self._infer_prop(_type)
        else:
            _prop = self._prop

        return constants.VIZ_PROPERTIES_MAP.get(_prop)

    def _check_type(self, _type):
        if _type and _type not in constants.LEGEND_TYPES:
            raise ValueError(
                'Legend type "{}" is not valid. Valid legend types are: {}.'.format(
                    _type, ', '.join(constants.LEGEND_TYPES)
                ))

    def _check_prop(self, _prop):
        if _prop and _prop not in constants.LEGEND_PROPERTIES:
            raise ValueError(
                'Legend property "{}" is not valid. Valid legend properties are: {}.'.format(
                    _prop, ', '.join(constants.LEGEND_PROPERTIES)
                ))

    def _infer_prop(self, _type):
        if _type.startswith('color'):
            return 'color'
        elif _type.startswith('size'):
            return 'size'
        else:
            return None

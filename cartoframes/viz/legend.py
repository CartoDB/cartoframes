from __future__ import absolute_import

from . import constants


class Legend(object):
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

    def __init__(self, f_arg, **kwargs):
        if isinstance(f_arg, str):
            self._init_legend(kwargs, f_arg)
        elif f_arg is None:
            self._init_legend(None)
        elif isinstance(f_arg, dict):
            self._init_legend(f_arg)
        else:
            raise ValueError('Wrong legend input.')

    def _init_legend(self, data, legend_type=None):
        self._type = ''
        self._prop = ''
        self._variable = ''
        self._dynamic = True
        self._title = ''
        self._description = ''
        self._footer = ''

        if data is not None:
            self._type = legend_type if legend_type else data.get('type', '')
            self._prop = data.get('prop', '')
            self._variable = data.get('variable', '')
            self._dynamic = data.get('dynamic', True)
            self._title = data.get('title', '')
            self._description = data.get('description', '')
            self._footer = data.get('footer', '')

    def get_info(self, geom_type=None):
        if self._type or self._title or self._description or self._footer:
            _type = self._get_type(geom_type)
            _prop = self._get_prop(_type)

            return {
                'type': _type,
                'prop': _prop,
                'variable': self._variable,
                'dynamic': self._dynamic,
                'title': self._title,
                'description': self._description,
                'footer': self._footer
            }
        else:
            return {}

    def _get_type(self, geom_type):
        if isinstance(self._type, dict) and geom_type in self._type:
            _type = self._type.get(geom_type)
        else:
            _type = self._type

        self._check_type(_type)
        return _type

    def _get_prop(self, _type):
        if _type and not self._prop:
            _prop = self._infer_prop(_type)
        else:
            _prop = self._prop

        self._check_prop(_prop)
        return _prop

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
            return 'width'
        else:
            return None

from __future__ import absolute_import

from ..utils import gen_variable_name


class Popup(object):
    """Popup

    Args:
        data (dict): The popup definition for a layer. It contains the information
          to show a popup on 'click' and 'hover' events with the attributes provided
          in the definition using the `CARTO VL expressions syntax
          <https://carto.com/developers/carto-vl/reference/#cartoexpressions>`.

    Example:

        Show columns.

        .. code::

            from cartoframes.viz import Popup

            Popup({
                'hover': ['$name'],
                'click': ['$name', '$pop_max']
            })

        Show expressions.

        .. code::

            from cartoframes.viz import Popup

            Popup({
                'click': ['$pop_min % 100', 'sqrt($pop_max)']
            })

        Show titles.

        .. code::

            from cartoframes.viz import Popup

            Popup({
                'hover': [{
                    'title': 'Name',
                    'value': '$name'
                }],
                'click': [{
                    'title': 'Name',
                    'value': '$name'
                }, {
                    'title': 'Pop max',
                    'value': '$pop_max'
                }]
            })

    """

    def __init__(self, data=None):
        self._init_popup(data)

    def _init_popup(self, data):
        self._click = []
        self._hover = []
        if data is not None:
            if isinstance(data, dict):
                # TODO: error control
                if 'click' in data:
                    click_data = data.get('click', [])
                    if isinstance(click_data, list):
                        self._click = click_data
                    else:
                        self._click = [click_data]
                if 'hover' in data:
                    hover_data = data.get('hover', [])
                    if isinstance(hover_data, list):
                        self._hover = hover_data
                    else:
                        self._hover = [hover_data]
            else:
                raise ValueError('Wrong popup input')

    def get_interactivity(self):
        interactivity = []
        if len(self._click) > 0:
            interactivity.append({
                'event': 'click',
                'attrs': self._get_attrs(self._click)
            })
        if len(self._hover) > 0:
            interactivity.append({
                'event': 'hover',
                'attrs': self._get_attrs(self._hover)
            })
        return interactivity

    def _get_attrs(self, array):
        output = []
        for item in array:
            if item:
                if isinstance(item, str):
                    output.append({
                        'name': gen_variable_name(item),
                        'title': item
                    })
                elif isinstance(item, dict) and 'value' in item:
                    output.append({
                        'name': gen_variable_name(item.get('value')),
                        'title': item.get('title')
                    })
                else:
                    raise ValueError('Wrong popup input')
        return output

    def get_variables(self):
        return self._get_vars(self._click + self._hover)

    def _get_vars(self, array):
        output = {}
        for item in array:
            if item:
                if isinstance(item, str):
                    name = gen_variable_name(item)
                    output[name] = item
                elif isinstance(item, dict) and 'value' in item:
                    name = gen_variable_name(item.get('value'))
                    output[name] = item.get('value')
                else:
                    raise ValueError('Wrong popup input')
        return output

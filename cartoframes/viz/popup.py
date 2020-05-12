from ..utils.utils import gen_variable_name


class Popup:
    """Popups can be added to each layer and displayed in the visualization when clicking or hovering
    features.

    They should be added by using the :py:meth:`popup_element <cartoframes.viz.popup_element>` in each
    Layer popup.

    """
    def __init__(self, event=None, value=None, title=None, format=None):
        self._init_popup(event, value, title, format)

    def _init_popup(self, event=None, value=None, title=None, format=None):
        if not isinstance(event, str) and not isinstance(value, str):
            raise ValueError('Wrong popup input')

        self._event = event
        self._value = value
        self._title = title if title else value
        self._format = format

        self._interactivity = self._get_interactivity()
        self._variable = self._get_variable()

    @property
    def value(self):
        return self._value

    @property
    def title(self):
        return self._title

    @property
    def interactivity(self):
        return self._interactivity

    @property
    def variable(self):
        return self._variable

    def _get_interactivity(self):
        return {
            'event': self._event,
            'attrs': self._get_attrs()
        }

    def _get_attrs(self):
        return {
            'name': gen_variable_name(self._value),
            'title': self._title,
            'format': self._format
        }

    def _get_variable(self):
        return {
            'name': gen_variable_name(self._value),
            'value': self._value
        }

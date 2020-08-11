class Style:

    def __init__(self, data=None, value=None,
                 default_legend=None, default_widget=None,
                 default_popup_hover=None, default_popup_click=None):
        self._style = self._init_style(data=data)
        self._value = value
        self._default_legend = default_legend
        self._default_widget = default_widget
        self._default_popup_hover = default_popup_hover
        self._default_popup_click = default_popup_click

    def _init_style(self, data):
        if isinstance(data, (str, dict)):
            return data
        else:
            return None

    @property
    def value(self):
        return self._value

    @property
    def default_legend(self):
        return self._default_legend

    @property
    def default_widget(self):
        return self._default_widget

    @property
    def default_popup_hover(self):
        return self._default_popup_hover

    @property
    def default_popup_click(self):
        return self._default_popup_click

    def compute_viz(self, variables={}):
        if not self._style:
            return None

        name = self._style.get('name')
        value = self._style.get('value')
        options = {k: v for k, v in self._style.get('properties').items() if v is not None}

        style = {
            'name': name,
            'options': options
        }

        if value:
            style['value'] = value

        return style

import re

from .popup import Popup
from .styles.utils import prop


class PopupList:
    """PopupList

     Args:
        popups (dict, PopupElement): List of popups for a layer classified by interactivity event

    Example:
        >>> popupList = PopupList({
        ... 'click': [popup_element('name')],
        ... 'hover': [popup_element('pop_max')]
        >>> })

    """
    def __init__(self, popups=None, default_popup_hover=None, default_popup_click=None):
        self._popups = self._init_popups(popups, default_popup_hover, default_popup_click)

    def _init_popups(self, popups, default_popup_hover, default_popup_click):
        if isinstance(popups, dict):
            return self._get_popup_elements(popups, default_popup_hover, default_popup_click)
        else:
            return []

    @property
    def elements(self):
        return self._popups

    def _get_popup_elements(self, popups, default_popup_hover, default_popup_click):
        popup_elements = []
        click_popup_elements = popups.get('click')
        hover_popup_elements = popups.get('hover')

        if click_popup_elements is not None:
            if not isinstance(click_popup_elements, list):
                click_popup_elements = [click_popup_elements]
            click_popup_elements.reverse()
            for popup in click_popup_elements:
                if isinstance(popup, dict):
                    if popup.get('value') is None and default_popup_click:
                        popup['value'] = default_popup_click.get('value')
                    popup_elements.append(
                        Popup('click',
                              value=popup.get('value'),
                              title=popup.get('title'))
                    )

        if hover_popup_elements is not None:
            if not isinstance(hover_popup_elements, list):
                hover_popup_elements = [hover_popup_elements]
            hover_popup_elements.reverse()
            for popup in hover_popup_elements:
                if isinstance(popup, dict):
                    if popup.get('value') is None and default_popup_hover:
                        popup['value'] = default_popup_hover.get('value')
                    popup_elements.append(
                        Popup('hover',
                              value=popup.get('value'),
                              title=popup.get('title'))
                    )

        return popup_elements

    def get_interactivity(self):
        popups_interactivity = []

        for popup in self._popups:
            if popup:
                popups_interactivity.append(popup.interactivity)

        return popups_interactivity

    def get_variables(self):
        popups_variables = {}

        for popup in self._popups:
            if popup:
                name = popup.variable.get('name')
                value = popup.variable.get('value')
                if re.match(r'^cluster[a-zA-Z]+\(.*\)$', value):
                    popups_variables[name] = value
                else:
                    popups_variables[name] = prop(value)

        return popups_variables

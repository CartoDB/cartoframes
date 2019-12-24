from __future__ import absolute_import

from .popup import Popup


class PopupList:
    """PopupList

     Args:
        popups (dict, PopupElement): List of popups for a layer classified by interactivity event

    Example:

        .. code::

        popupList = PopupList({
            'click': [popup_element('name')],
            'hover': [popup_element('pop_max')]
        })
    """

    def __init__(self, popups=None):
        self._popups = self._init_popups(popups)

    def _init_popups(self, popups):
        if isinstance(popups, dict):
            return self.get_popup_elements(popups)
        else:
            return []

    @property
    def elements(self):
        return self._popups

    def get_popup_elements(self, popups):
        popup_elements = []
        click_popup_elements = popups.get('click')
        hover_popup_elements = popups.get('hover')

        if click_popup_elements is not None:
            if not isinstance(click_popup_elements, list):
                click_popup_elements = [click_popup_elements]
            for popup in click_popup_elements:
                popup_elements.append(
                    Popup('click',
                          value=popup.get('value'),
                          title=popup.get('title'),
                          operation=popup.get('operation', False))
                )

        if hover_popup_elements is not None:
            if not isinstance(hover_popup_elements, list):
                hover_popup_elements = [hover_popup_elements]
            for popup in hover_popup_elements:
                popup_elements.append(
                    Popup('hover',
                          value=popup.get('value'),
                          title=popup.get('title'),
                          operation=popup.get('operation', False))
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
                popups_variables[popup.variable.get('name')] = popup.variable.get('value')

        return popups_variables

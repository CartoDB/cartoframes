from __future__ import absolute_import

from .popup import Popup


class PopupList(object):
    """PopupList

     Args:
        popups (list, Popup): List of popups for a layer.
    """

    def __init__(self, popups=None):
        self._popups = self._init_popups(popups)

    def _init_popups(self, popups):
        if isinstance(popups, list):
            popup_list = []
            for popup in popups:
                if isinstance(popup, Popup):
                    popup_list.append(popup)
                else:
                    raise ValueError('All PopupList elements must be Popups')
            return popup_list
        elif isinstance(popups, Popup):
            return [popups]
        else:
            return []

    def get_interactivity(self):
        popups_interactivity = []

        for popup in self._popups:
            if popup:
                popups_interactivity.append(popup.get_interactivity())

        return popups_interactivity

    def get_variables(self):
        popups_variables = {}

        for popup in self._popups:
            if popup:
                variable = popup.get_variables()
                popups_variables[variable.get('name')] = variable.get('value')

        return popups_variables

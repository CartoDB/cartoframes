from __future__ import absolute_import

from ..popup import Popup


def click_popup(value=None, title=None, operation=False):
    return Popup('click', value, title, operation)

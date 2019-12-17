from __future__ import absolute_import

from ..popup import Popup


def hover_popup(value=None, title=None, operation=False):
    return Popup('hover', value, title, operation)

from __future__ import absolute_import

from ..popup import Popup


def hover_popup(value=None, title=None):
    return Popup('hover', value, title)

from __future__ import absolute_import
from ..utils import defaults


class Source(object):
    """CARTO VL Source:

      Args:
        - dataset.
        - bounds (dict): Viewport bounds.
    """

    def __init__(self, dataset, bounds=None):
        self.dataset = dataset
        self.bounds = bounds
        self.type = dataset.type
        self.query = dataset.query
        self.context = dataset.cc
        
        if dataset.cc.creds is not None:
            self.credentials = {
                'username': dataset.cc.creds.username(),
                'api_key': dataset.cc.creds.key(),
                'base_url': dataset.cc.creds.base_url()
            }
        else:
            self.credentials = defaults._CREDENTIALS



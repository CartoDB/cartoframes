from __future__ import absolute_import


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

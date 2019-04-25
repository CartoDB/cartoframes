from __future__ import absolute_import
from .source import Source


class Dataset(Source):
    """
      TODO
    """

    def __init__(self, dataset):
        query = 'SELECT * FROM {}'.format(dataset)
        super(Dataset, self).__init__(query)

from abc import ABCMeta, abstractmethod

class DatasetBase():
    __metaclass__ = ABCMeta

    FAIL = 'fail'
    REPLACE = 'replace'
    APPEND = 'append'

    PRIVATE = DatasetInfo.PRIVATE
    PUBLIC = DatasetInfo.PUBLIC
    LINK = DatasetInfo.LINK

    STATE_LOCAL = 'local'
    STATE_REMOTE = 'remote'

    GEOM_TYPE_POINT = 'point'
    GEOM_TYPE_LINE = 'line'
    GEOM_TYPE_POLYGON = 'polygon'

    def __init__(self, data):
        from ..auth import _default_context
        self._context = _default_context

        self.data = data

        self._client = self._get_client()

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    def get_data(self):
        return self.data

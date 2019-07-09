from abc import ABCMeta, abstractmethod

class DatasetBase():
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.data = data

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

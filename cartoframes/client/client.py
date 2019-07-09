from abc import ABCMeta, abstractmethod


class ClientBase(metaclass=ABCMeta):
    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def execute_query(self):
        pass

    @abstractmethod
    def execute_long_running_query(self):
        pass

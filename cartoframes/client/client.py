from abc import ABC, abstractmethod


class ClientBase(ABC):
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

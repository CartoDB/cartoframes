from abc import ABCMeta, abstractmethod

from api_client import APIClient


def get_client(self, creds, session):
    return APIClient(creds, session)


class ClientBase(metaclass=ABCMeta):
    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass





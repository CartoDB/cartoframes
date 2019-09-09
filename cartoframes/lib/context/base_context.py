from abc import ABCMeta, abstractmethod


class BaseContext():
    __metaclass__ = ABCMeta

    @abstractmethod
    def download(self, query, retry_times=0):
        pass

    @abstractmethod
    def upload(self, query, data):
        pass

    @abstractmethod
    def execute_query(self, query, parse_json=True, do_post=True, format=None, **request_args):
        pass

    @abstractmethod
    def execute_long_running_query(self, query):
        pass

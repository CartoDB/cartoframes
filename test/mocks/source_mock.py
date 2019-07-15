from cartoframes.viz import Source
from mocks.context_mock import ContextMock
from mocks.dataset_mock import DatasetMock


class SourceMock(Source):
    def _init_source_table(self, data, context, schema, bounds):
        username = 'fake_username'
        api_key = 'fake_api_key'
        context = ContextMock(username=username, api_key=api_key)

        self.dataset = DatasetMock(data, context, schema)
        self._set_source_query(self.dataset, bounds)

    def _init_source_query(self, data, context, bounds):
        username = 'fake_username'
        api_key = 'fake_api_key'
        context = ContextMock(username=username, api_key=api_key)

        self.dataset = DatasetMock(data, context)
        self._set_source_query(self.dataset, bounds)

from .context_mock import ContextMock

def mock_create_context(mocker, response=''):
    context_mock = ContextMock(response)
    mocker.spy(context_mock, 'execute_query')
    mocker.patch(
        'cartoframes.lib.context.create_context',
        return_value=context_mock)
    return context_mock

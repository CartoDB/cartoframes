from cartoframes.core.managers.context_manager import ContextManager


def setup_mocks(mocker, geom_type='point'):
    mocker.patch.object(ContextManager, 'compute_query')
    mocker.patch.object(ContextManager, 'get_geom_type', return_value=geom_type)
    mocker.patch.object(ContextManager, 'get_bounds')

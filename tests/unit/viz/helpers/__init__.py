from cartoframes.viz import Source


def setup_mocks(mocker, geom_type='point'):
    mocker.patch.object(Source, 'get_geom_type', return_value=geom_type)
    mocker.patch.object(Source, '_compute_query_bounds')

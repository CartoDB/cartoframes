from cartoframes import CartoContext

def exampleContext():
    """Returns a CartoContext corresponding to a CARTO account with example data"""
    return CartoContext(base_url='https://cartoframes.carto.com', api_key='default_public')

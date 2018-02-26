"""example data factory"""
from cartoframes import CartoContext

# EXAMPLE_BASE_URL = 'https://cartoframes.carto.com'
# EXAMPLE_API_KEY = 'default_public'
EXAMPLE_BASE_URL = 'http://cdb.localhost.lan:8888/'
EXAMPLE_API_KEY = 'default_public'


def example_context():
    """Returns a CartoContext with a CARTO account containing example data"""
    return CartoContext(base_url=EXAMPLE_BASE_URL, api_key=EXAMPLE_API_KEY)

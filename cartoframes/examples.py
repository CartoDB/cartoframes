"""example data factory"""
from cartoframes import CartoContext

EXAMPLE_BASE_URL = 'https://cartoframes.carto.com'
EXAMPLE_API_KEY = 'default_public'
# EXAMPLE_BASE_URL = 'http://cdb.localhost.lan:8888/'
# EXAMPLE_API_KEY = 'default_public'


class Examples(CartoContext):
    """A CartoContext with a CARTO account containing example data"""
    def __init__(self):
        super(Examples, self). \
            __init__(base_url=EXAMPLE_BASE_URL, api_key=EXAMPLE_API_KEY)

    def read_taxi(self):
        return self.read('taxi_dataset')

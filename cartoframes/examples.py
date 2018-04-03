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
        return self.read('taxi_50k')

    def data(self):
        raise RuntimeError('data function disabled for Examples')

    def write(self, df, table_name, temp_dir=None, overwrite=False,
              lnglat=None, encode_geom=False, geom_col=None,
              **kwargs):
        raise RuntimeError('write function disabled for Examples')

    def data_boundaries(self, boundary=None, region=None, decode_geom=False,
                        timespan=None, include_nonclipped=False):
        raise RuntimeError('data_boundaries function disabled for Examples')

    def data_discovery(self, region, keywords=None, regex=None, time=None,
                       boundaries=None, include_quantiles=False):
        raise RuntimeError('data_discovery function disabled for Examples')

    def data_augment(self, table_name, metadata):
        raise RuntimeError('data_augment function disabled for Examples')


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

    # example dataset read methods
    def read_brooklyn_poverty(self, limit=None, **kwargs):
        return self.read('brooklyn_poverty', limit, **kwargs)

    def read_mcdonalds_nyc(self, limit=None, **kwargs):
        return self.read('mcdonalds_nyc', limit, **kwargs)

    def read_nyc_census_tracts(self, limit=None, **kwargs):
        return self.read('nyc_census_tracts', limit, **kwargs)

    def read_taxi(self, limit=None, **kwargs):
        return self.read('taxi_50k', limit, **kwargs)

    def read_nat(self, limit=None, **kwargs):
        return self.read('nat', limit, **kwargs)

    # override behavior of CartoContext methods
    def data(self):
        raise RuntimeError('CartoContext.data method disabled for Examples')

    def write(self, df, table_name, temp_dir=None, overwrite=False,
              lnglat=None, encode_geom=False, geom_col=None,
              **kwargs):
        raise RuntimeError('CartoContext.write method disabled for Examples')

    def data_boundaries(self, boundary=None, region=None, decode_geom=False,
                        timespan=None, include_nonclipped=False):
        raise RuntimeError(
            'CartoContext.data_boundaries method disabled for Examples')

    def data_discovery(self, region, keywords=None, regex=None, time=None,
                       boundaries=None, include_quantiles=False):
        raise RuntimeError(
            'CartoContext.data_discovery method disabled for Examples')

    def data_augment(self, table_name, metadata):
        raise RuntimeError(
            'CartoContext.data_augment method disabled for Examples')


example_context = Examples()

def read_brooklyn_poverty(limit=None, **kwargs):
    """Read the dataset `brooklyn_poverty` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/brooklyn_poverty/public
    This dataset contains poverty rates for census tracts in Brooklyn, New York

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in `CartoContext.read`

    Returns:

      pandas.Dataframe: Data in the table `brooklyn_poverty` on the CARTOframes
        example account

    Example:

    .. code::

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty(decode_geom=True)

    """
    return example_context.read_brooklyn_poverty(limit=limit, **kwargs)

def read_mcdonalds_nyc(limit=None, **kwargs):
    """Read the dataset `nyc_mcdonalds` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/nyc_mcdonalds/public
    This dataset contains the locations of McDonald's Fast Food within New York
    City.

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in `CartoContext.read`

    Returns:

      pandas.Dataframe: Data in the table `nyc_mcdonalds` on the CARTOframes
        example account

    Example:

    .. code::

        from cartoframes.examples import read_mcdonalds_nyc
        df = read_mcdonalds_nyc(decode_geom=True)

    """
    return example_context.read_mcdonalds_nyc(limit=limit, **kwargs)

def read_nyc_census_tracts(limit=None, **kwargs):
    """Read the dataset `nyc_census_tracts` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/nyc_census_tracts/public
    This dataset contains the US census boundaries for 2015 Tiger census
    tracts and the corresponding GEOID in the `geom_refs` column.

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in `CartoContext.read`

    Returns:

      pandas.Dataframe: Data in the table `nyc_census_tracts` on the
        CARTOframes example account

    Example:

    .. code::

        from cartoframes.examples import read_nyc_census_tracts
        df = read_nyc_census_tracts(decode_geom=True)

    """
    return example_context.read_nyc_census_tracts(limit=limit, **kwargs)

def read_taxi(limit=None, **kwargs):
    """Read the dataset `taxi_50k` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/taxi_50k/public. This table
    has a sample of 50,000 taxi trips taken in New York City. The dataset
    includes fare amount, tolls, payment type, and pick up and drop off
    locations. Note: the geometry has to be created by using the pickup or
    drop off lng/lat pairs. These can be specified in `CartoContext.write`.

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in `CartoContext.read`

    Returns:

      pandas.Dataframe: Data in the table `taxi_50k` on the CARTOframes
        example account

    Example:

    .. code::

        from cartoframes.examples import read_taxi
        df = read_taxi(decode_geom=True)

    """
    return example_context.read_taxi(limit=limit, **kwargs)

def read_nat(limit=None, **kwargs):
    """Read `nat` dataset: US county homicides 1960-1990

    This table is located at:
    https://cartoframes.carto.com/tables/nat/public
    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in `CartoContext.read`

    Returns:

      pandas.Dataframe: Data in the table `taxi_50k` on the CARTOframes
        example account

    Example:

    .. code::

        from cartoframes.examples import read_taxi
        df = read_taxi(decode_geom=True)
    """
    return example_context.read_nat(limit=limit, **kwargs)

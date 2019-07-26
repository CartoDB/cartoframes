"""Download, preview, and query example datasets for use in cartoframes
examples. Try examples by `running the notebooks in binder
<https://mybinder.org/v2/gh/CartoDB/cartoframes/master?filepath=examples>`__

In addition to the functions listed below, this examples module is
authenticated against all public datasets in the https://cartoframes.carto.com
account. This means that besides reading the datasets from CARTO, users can
also create maps from these datasets.

For example, the following will produce an interactive map of poverty rates in
census tracts in Brooklyn, New York (preview of static version below code).

    .. code::

        from cartoframes.examples import examples

        examples.map('brooklyn_poverty')

.. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels1_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_nolabels%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++polygon-fill%3A+ramp%28%5Bpoverty_per_pop%5D%2C+cartocolor%28Mint%29%2C+quantiles%285%29%2C+%3E%29%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D%23layer%5Bpoverty_per_pop+%3D+null%5D+%7B++polygon-fill%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+brooklyn_poverty%22%7D&anti_cache=0.2903456538919632&bbox=-74.041916%2C40.569596%2C-73.833422%2C40.739158

To query datasets, use the :py:class:`Dataset <cartoframes.data.Dataset>` class.
The following example finds the poverty rate in the census tract a McDonald's fast
food joint is located (preview of static map below code).

    .. code::

        from cartoframes.examples import examples
        from cartoframes.data import Dataset

        # query to get poverty rates where mcdonald's are located in brooklyn
        query = '''
                    SELECT m.the_geom, m.cartodb_id, m.the_geom_webmercator, c.poverty_per_pop
                    FROM mcdonalds_nyc as m, brooklyn_poverty as c WHERE ST_Intersects(m.the_geom, c.the_geom)
                '''

        credentials = examples.get_credentials()
        ds = Dataset(query, credentials=credentials)

        # download and show the data
        ds.download()
        ds.dataframe

        # map
        examples.map(ds)

.. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels0_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++marker-width%3A+ramp%28%5Bpoverty_per_pop%5D%2C+range%285%2C25%29%2C+quantiles%285%29%29%3B+marker-fill%3A+%235D69B1%3B+marker-fill-opacity%3A+0.9%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23FFF%3B+marker-line-opacity%3A+1%3B%7D%22%2C+%22sql_0%22%3A+%22%5CnSELECT+m.the_geom%2C+m.cartodb_id%2C+m.the_geom_webmercator%2C+c.poverty_per_pop%5CnFROM+mcdonalds_nyc+as+m%2C+brooklyn_poverty+as+c%5CnWHERE+ST_Intersects%28m.the_geom%2C+c.the_geom%29%5Cn%22%7D&anti_cache=0.040403611167980635&bbox=-74.0277516749999%2C40.57955036%2C-73.8603420299999%2C40.7303652850001


To write datasets to your account from the examples account, the following is a
good method:

    .. code::

        from cartoframes.auth import Credentials
        from cartoframes.data import Dataset
        from cartoframes.examples import read_taxi

        USERNAME = 'your user name'
        APIKEY = 'your API key'

        credentials = Credentials(
            username=USERNAME,
            api_key=APIKEY
        )

        Dataset(read_taxi()).upload(
          table_name='taxi_data_examples_acct',
          lnglat=('pickup_latitude', 'pickup_longitude')
          credentials=credentials)
"""  # noqa
from cartoframes.auth import Credentials
from cartoframes.data import Dataset, tables
from cartoframes.viz import Map, Layer

EXAMPLE_BASE_URL = 'https://cartoframes.carto.com'
EXAMPLE_API_KEY = 'default_public'


class Examples():
    """This special class provides read access to all the datasets in the cartoframes CARTO account.

    The recommended way to use this class is to import the `examples`
    from the `cartoframes.examples` module:

    .. code::

        from cartoframes.examples import examples
        df = examples.read_taxi()

    The following tables are available:

    - ``brooklyn_poverty`` - basic poverty information for Brooklyn, New York
    - ``mcdonalds_nyc`` - McDonald's locations in New York City
    - ``nat`` - historical USA-wide homicide rates at the county level
    - ``nyc_census_tracts`` - Census tract boundaries for New York City
    - ``taxi_50k`` - Taxi trip data, including pickup/drop-off locations. This
      table does not have an explicit geometry, so one must be created from the
      `pickup_latitude`/`pickup_longitude` columns, the
      `dropoff_latitude`/`dropoff_longitude` columns, or through some other
      process. When writing this table to your account, make sure to specify
      the `lnglat` flag in :py:meth:`Dataset.upload
      <cartoframes.data.Dataset.upload>`

    This class includes a convenience method for each of the tables listed above.
    See the full list below.

    """

    def __init__(self):
        self._credentials = Credentials(base_url=EXAMPLE_BASE_URL, api_key=EXAMPLE_API_KEY)

    # example dataset read methods
    def read_brooklyn_poverty(self, limit=None, **kwargs):
        """Poverty information for Brooklyn, New York, USA. See the function
        :py:func:`read_brooklyn_poverty
        <cartoframes.examples.read_brooklyn_poverty>` for more information.

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_brooklyn_poverty()

        """
        return Dataset('brooklyn_poverty', self._credentials).download(limit, **kwargs)

    def read_ne_50m_graticules_15(self, limit=None, **kwargs):
        """50m world Mercator grid
        <cartoframes.examples.read_ne_50m_graticules_15>` for more information.

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_ne_50m_graticules_15()

        """
        return Dataset('ne_50m_graticules_15', self._credentials).download(limit, **kwargs)

    def read_mcdonalds_nyc(self, limit=None, **kwargs):
        """McDonald's locations for New York City, USA. See the function
        :py:func:`read_mcdonalds_nyc
        <cartoframes.examples.read_mcdonalds_nyc>` for more information

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_mcdonalds_nyc()

        """
        return Dataset('mcdonalds_nyc', self._credentials).download(limit, **kwargs)

    def read_nyc_census_tracts(self, limit=None, **kwargs):
        """Census tracts for New York City, USA. See the function
        :py:func:`read_nyc_census_tracts
        <cartoframes.examples.read_nyc_census_tracts>` for more information

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_nyc_census_tracts()

        """
        return Dataset('nyc_census_tracts', self._credentials).download(limit, **kwargs)

    def read_taxi(self, limit=None, **kwargs):
        """Taxi pickup and drop-off logs for New York City, USA. See the
        function :py:func:`read_taxi
        <cartoframes.examples.read_taxi>` for more information

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_taxi()

        """
        return Dataset('taxi_50k', self._credentials).download(limit, **kwargs)

    def read_nat(self, limit=None, **kwargs):
        """Historical homicide rates for the United States at the county level.
        See the function :py:func:`read_nat
        <cartoframes.examples.read_nat>` for more information

        Example:

        .. code::

            from cartoframes.examples import examples
            df = examples.read_nat()

        """
        return Dataset('nat', self._credentials).download(limit, **kwargs)

    def tables(self):
        return tables(self._credentials)

    def map(self, source):
        return Map(Layer(source, credentials=self._credentials))

    def get_credentials(self):
        return self._credentials


examples = Examples()


def read_ne_50m_graticules_15(limit=None, **kwargs):
    """Read the dataset `ne_50m_graticules_15` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/ne_50m_graticules_15/public
    This dataset contains a 50m world Mercator grid

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `ne_50m_graticules_15` on the cartoframes
      example account

    Example:

    .. code::

        from cartoframes.examples import read_ne_50m_graticules_15
        df = read_ne_50m_graticules_15()

    """
    return examples.read_ne_50m_graticules_15(limit=limit, **kwargs)


def read_brooklyn_poverty(limit=None, **kwargs):
    """Read the dataset `brooklyn_poverty` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/brooklyn_poverty/public
    This dataset contains poverty rates for census tracts in Brooklyn, New York

    The data looks as follows (styled on `poverty_per_pop`):

    .. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels1_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_nolabels%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++polygon-fill%3A+ramp%28%5Bpoverty_per_pop%5D%2C+cartocolor%28Mint%29%2C+quantiles%285%29%2C+%3E%29%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D%23layer%5Bpoverty_per_pop+%3D+null%5D+%7B++polygon-fill%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+brooklyn_poverty%22%7D&anti_cache=0.10952614318949128&bbox=-74.041916%2C40.569596%2C-73.833422%2C40.739158

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `brooklyn_poverty` on the cartoframes
      example account

    Example:

    .. code::

        from cartoframes.examples import read_brooklyn_poverty
        df = read_brooklyn_poverty()

    """  # noqa
    return examples.read_brooklyn_poverty(limit=limit, **kwargs)


def read_mcdonalds_nyc(limit=None, **kwargs):
    """Read the dataset `mcdonalds_nyc` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/mcdonalds_nyc/public
    This dataset contains the locations of McDonald's Fast Food within New York
    City.

    Visually the data looks as follows:

    .. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels0_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++marker-width%3A+10%3B+marker-fill%3A+%235D69B1%3B+marker-fill-opacity%3A+0.9%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23FFF%3B+marker-line-opacity%3A+1%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+mcdonalds_nyc%22%7D&anti_cache=0.5738692383372218&bbox=-74.1691323509999%2C40.5594463460001%2C-73.7431178569999%2C40.892981078

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `mcdonalds_nyc` on the cartoframes
      example account

    Example:

    .. code::

        from cartoframes.examples import read_mcdonalds_nyc
        df = read_mcdonalds_nyc()

    """  # noqa
    return examples.read_mcdonalds_nyc(limit=limit, **kwargs)


def read_nyc_census_tracts(limit=None, **kwargs):
    """Read the dataset `nyc_census_tracts` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/nyc_census_tracts/public
    This dataset contains the US census boundaries for 2015 Tiger census
    tracts and the corresponding GEOID in the `geom_refs` column.

    Visually the data looks as follows:

    .. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels1_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_nolabels%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++polygon-fill%3A+%235D69B1%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+nyc_census_tracts%22%7D&anti_cache=0.05019415422872964&bbox=-74.25909%2C40.477399%2C-73.70002%2C40.917577

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `nyc_census_tracts` on the
      cartoframes example account

    Example:

    .. code::

        from cartoframes.examples import read_nyc_census_tracts
        df = read_nyc_census_tracts()

    """  # noqa
    return examples.read_nyc_census_tracts(limit=limit, **kwargs)


def read_taxi(limit=None, **kwargs):
    """Read the dataset `taxi_50k` into a pandas DataFrame from the
    cartoframes example account at
    https://cartoframes.carto.com/tables/taxi_50k/public. This table
    has a sample of 50,000 taxi trips taken in New York City. The dataset
    includes fare amount, tolls, payment type, and pick up and drop off
    locations.

    .. note:: This dataset does not have geometries. The geometries have to be
        created by using the pickup or drop-off lng/lat pairs. These can be
        specified in `Dataset.upload`.

        To create geometries with `examples.query`, write a query such
        as this::

            from cartoframes.client import SQLClient

            sql = SQLClient(examples.get_credentials())

            sql.query('''
                SELECT
                  CDB_LatLng(pickup_latitude, pickup_longitude) as the_geom,
                  cartodb_id,
                  fare_amount
                FROM
                  taxi_50
            ''')

    The data looks as follows (using the pickup location for the geometry and
    styling by `fare_amount`):

    .. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++marker-width%3A+10%3B+marker-fill%3A+ramp%28%5Bfare_amount%5D%2C+cartocolor%28Mint%29%2C+quantiles%285%29%2C+%3E%29%3B+marker-fill-opacity%3A+0.9%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23FFF%3B+marker-line-opacity%3A+1%3B%7D%23layer%5Bfare_amount+%3D+null%5D+%7B++marker-fill%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22%5Cn++++WITH+cte+as+%28%5Cn++++SELECT+CDB_LatLng%28pickup_latitude%2C+pickup_longitude%29+as+the_geom%2C+cartodb_id%2C+fare_amount%5Cn++++FROM+taxi_50k%5Cn++++%29%5Cn++++SELECT+%2A%2C+ST_Transform%28the_geom%2C+3857%29+as+the_geom_webmercator%5Cn++++FROM+cte%5Cn%22%7D&anti_cache=0.24523273064119488&zoom=9&lat=40.7743&lon=-73.916

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `taxi_50k` on the cartoframes
      example account

    Example:

    .. code::

        from cartoframes.examples import read_taxi
        df = read_taxi()

    """  # noqa
    return examples.read_taxi(limit=limit, **kwargs)


def read_nat(limit=None, **kwargs):
    """Read `nat` dataset: US county homicides 1960-1990

    This table is located at:
    https://cartoframes.carto.com/tables/nat/public

    Visually, the data looks as follows (styled by the `hr90` column):

    .. image:: https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels1_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_nolabels%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++polygon-fill%3A+ramp%28%5Bhr90%5D%2C+cartocolor%28Sunset%29%2C+quantiles%287%29%2C+%3E%29%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D%23layer%5Bhr90+%3D+null%5D+%7B++polygon-fill%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+nat%22%7D&anti_cache=0.9906959573885755&bbox=-124.731422424316%2C24.9559669494629%2C-66.9698486328125%2C49.3717346191406

    Args:

      limit (int, optional): Limit results to `limit`. Defaults to return all
        rows of the original dataset
      **kwargs: Arguments accepted in :py:meth:`Dataset.download <cartoframes.data.Dataset.download>`

    Returns:

      pandas.DataFrame: Data in the table `nat` on the cartoframes
      example account

    Example:

    .. code::

        from cartoframes.examples import read_nat
        df = read_nat()

    """  # noqa
    return examples.read_nat(limit=limit, **kwargs)

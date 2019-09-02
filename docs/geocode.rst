Geocode
=======

The ``GeocodeAnalysis`` class provides geocoding using CARTO LDS.
This analysis requires you to have a CARTO account with a geocoding provider and geocoding quota assigned, and its use will incurr in the expense of geocoding credits.
In the case of accounts with soft geocoding limits, additional charges may apply if the monthly quota is exceeded.

Input data to be geocoded must be provided through a ``Dataset`` object. The ``preview`` method will inform about the quota needed for
a geocoding operation; it won't effect any actual changes nor consume any quota:

.. code:: python

    from cartoframes.analysis import GeocodeAnalysis
    from cartoframes.data import Dataset

    dataset = Dataset('my_data')
    preview = geocoder.preview(dataset, street='address', country='country')
    print(preview.get('required_quota'))

When you're ready to perform the actual geocoding (and consume some quota!) there are three options:

Geocode *in-place* (``geocode()``), only possible for table datasets, will modify the dataset setting the geometry and a new column:
a internal-use hash column (to avoid unneccesary credit consumption is future geocodings).
Example:

.. code:: python

    dataset = Dataset('my_data')
    result = geocoder.geocode(dataset, street='address', country='country')
    print(result.get('required_quota'))

Geocode into a new dataframe (``geocoded_as_dataframe()``): the input can be a table, a query or a dataframe; it won't be modified in any way.
The result will contain a hash table; if that column is preseverved and used in future geocodings it will prevent
records that haven't changed from being geocoded again.

.. code:: python

    import pandas
    places = pandas.read_csv("https://storage.googleapis.com/test_carto/carto_places.csv")
    result = geocoder.geocoded_as_dataframe(dataset, street='address', country='country')
    print result.get('result').head

Geocode into a new table (``geocoded_as_table()``): the input can be a table, a query or a dataframe; it won't be modified in any way.
The result will contain a hash table; if that column is preseverved and used in future geocodings it will prevent
records that haven't changed from being geocoded again.

.. code:: python

    dataset = Dataset('SELECT * FROM my_data WHERE value > 100')
    result = geocoder.geocoded_as_table(dataset, street='address', country='country')
    print result.get('result').download().head

The ``cartoframes.data.dataservices.Geocode`` class provides geocoding using  `CARTO Location Data Services (LDS) <https://carto.com/location-data-services/>`_
This process requires you to have a CARTO account with a geocoding provider and geocoding quota assigned, and its use will incur in the expense of geocoding credits.
In the case of accounts with soft geocoding limits, additional charges may apply if the monthly quota is exceeded.

The ``Geocode.geocode`` instance method provides the interface to geocoding; input data to be geocoded must be provided through a ``Dataset`` or ``DataFrame`` object as the first argument to this method.
A second mandatory argument, ``street`` defines the name of the data column that contains the street address.

Additional optional arguments can be used to define the ``city``, ``state`` and ``country``. These arguments can be used to either
pass the name of a column that contains the corresponding attribute; e.g. ``city={'column': 'column_name_of_the_city'}``, which can
be shortened as  ``city='column_name_of_the_city'``,
or, when all the dataset corresponds to a single value of the attribute, a literal text, e.g. ``city={'value': 'London}'``.

Another optional argument, ``metadata`` can define the name of a result column that will contain additional metadata about each gecododed row
as a JSON structure. The entries in this structure, as described in https://carto.com/developers/data-services-api/reference/ are:


+-------------+--------+------------------------------------------------------------+
| Name        | Type   | Description                                                |
+=============+========+============================================================+
| precision   | text   | precise or interpolated                                    |
+-------------+--------+------------------------------------------------------------+
| relevance   | number | 0 to 1, higher being more relevant                         |
+-------------+--------+------------------------------------------------------------+
| match_types | array  | list of match type strings                                 |
|             |        | point_of_interest, country, state, county, locality,       |
|             |        | district, street, intersection, street_number, postal_code |
+-------------+--------+------------------------------------------------------------+


The result of the ``geocode`` method is a tuple containing both a result Dataset
(or a Dataframe, in case the input was a Dataframe) and a dictionary with general information about the process.

Dry run
"""""""

To find out the number of quota credits that will be spent when geocoding a dataset pass a ``dry_run=True`` argument:

.. code:: python

    from cartoframes.data.services import Geocode
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocode()

    dataset = Dataset('YOUR_DATA')
    _, info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'}, dry_run=True)
    print(info.get('required_quota'))

When ``dry_run`` is True no changes will be made to the data and no quota will be consumed.

Geocoding Dataframes
""""""""""""""""""""

A Dataframe can be geocoded like this:

.. code:: python

    import pandas
    from cartoframes.data.services import Geocode
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocode()

    df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

    geocoded_dataframe, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, metadata='meta')
    print(info)
    print(geocoded_dataframe)
    # Filtering by relevance
    print(geocoded_dataframe[geocoded_dataframe.apply(lambda x: json.loads(x['meta'])['relevance']>0.7, axis=1)])

To store the results permanently in a CARTO dataset the argument ``table_name`` can be used:

.. code:: python

    # ...
    geocoded_dataset, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, table_name='new_table')
    print(info)
    print(geocoded_dataset.download())

Geocoding Tables
""""""""""""""""

When the Dataset to be geocoded corresponds to a CARTO table, it will by default be modified in place:

.. code:: python

    import pandas
    from cartoframes.data.services import Geocode
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocode()

    dataset = Dataset('YOUR_DATA')
    dataset, info = gc.geocode(dataset, street='address', country={'value': 'Spain'})
    print(info)
    print(dataset.download())

To leave the existing table unmodified and place the results in a new table the ``table_name`` argument can be used:

.. code:: python

    # ...
    dataset = Dataset('YOUR_DATA')
    new_dataset, info = gc.geocode(dataset, street='address', country={'value': 'Spain'}, table_name='new_table')
    print(info)
    print(new_dataset.download())

Geocoding Queries
"""""""""""""""""

When the Dataset to be geocoded corresponds to a query, it will by default be geocoded into a new dataframe dataset:

.. code:: python

    import pandas
    from cartoframes.data.services import Geocode
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocode()

    dataset = Dataset('SELECT * FROM YOUR_DATA WHERE value>1000')
    ds, info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'})
    geocoded_dataset, info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'})
    print(info)
    print(geocoded_dataset.dataframe)

Again, the results can be stored in a new table using the `table_name` argument:

.. code:: python

    # ...
    dataset = Dataset('SELECT * FROM YOUR_DATA WHERE value>1000')
    new_dataset, info = gc.geocode(dataset, street='address', country={'value': 'Spain'}, table_name='new_table')
    print(info)
    print(new_dataset.download())

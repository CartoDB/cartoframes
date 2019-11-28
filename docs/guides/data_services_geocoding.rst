Geocoding
^^^^^^^^^

The ``cartoframes.data.services.Geocoding`` class provides geocoding using
`CARTO Location Data Services (LDS) <https://carto.com/location-data-services/>`_
This process requires you to have a CARTO account with a geocoding provider and geocoding quota assigned,
and its use will incur in the expense of geocoding credits.
In the case of accounts with soft geocoding limits, additional charges may apply if the monthly quota is exceeded.

The ``Geocoding.geocode`` instance method provides the interface to geocoding; input data to be geocoded must be
provided through a ``Dataset`` or ``DataFrame`` object as the first argument to this method.

A second mandatory argument, ``street`` defines the name of the data column that contains the street address.

Additional optional arguments can be used to define the ``city``, ``state`` and ``country``. These arguments can be
used to either pass the name of a column that contains the corresponding attribute;
e.g. ``city={'column': 'column_name_of_the_city'}``, which can be shortened as  ``city='column_name_of_the_city'``,
or, when all the dataset corresponds to a single value of the attribute, a literal text,
e.g. ``city={'value': 'London}'``.

For each geocoded record, some status information is available, as described in
https://carto.com/developers/data-services-api/reference/

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

By default the ``relevance`` is stored in an output column named ``gc_status_rel``. The name of the
column and in general what attributes are added as columns can be configured by using a ``status`` dictionary
associating column names to status attribute.

The result of the ``geocode`` method is a named tuple containing both a result ``data``
(of same class as the input, ``Dataframe``or ``Dataframe``) and a ``metadata`` dictionary with general
information about the process.

Dry run
"""""""

To find out the number of quota credits that will be spent when geocoding a dataset pass a ``dry_run=True`` argument:

.. code:: python

    from cartoframes.data.services import Geocoding
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocoding()

    dataset = Dataset('YOUR_DATA')
    info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'}, dry_run=True).metadata
    print(info.get('required_quota'))

When ``dry_run`` is True no changes will be made to the data and no quota will be consumed.
The returned dataset will simply be a reference to the input dataset, unmodified.

To know the quota available in the account used, the method ``available_quota`` can be used:

.. code:: python

    print(gc.available_quota())


Geocoding Dataframes
""""""""""""""""""""

A Dataframe can be geocoded like this:

.. code:: python

    import pandas
    from cartoframes.data.services import Geocoding
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocoding()

    df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

    geocoded_dataframe, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'})
    print(info)
    print(geocoded_dataframe)
    # Filtering by relevance
    print(geocoded_dataframe[geocoded_dataframe['gc_status_rel']>0.7])

To specify the status attributes and column names explicitly use the ``status`` argument:

.. code:: python

    geocoded_dataframe, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status={'relev':'relevance'})
    print(geocoded_dataframe[geocoded_dataframe['relev']>0.7])

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
    from cartoframes.data.services import Geocoding
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocoding()

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
    from cartoframes.data.services import Geocoding
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    gc = Geocoding()

    dataset = Dataset('SELECT * FROM YOUR_DATA WHERE value>1000')
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

Saving Quota
""""""""""""

To prevent having to geocode records that have been previously geocoded, and thus spend quota unnecessarily,
you should always preserve the ``the_geom`` and ``carto_geocode_hash`` columns generated by the
geocoding process. This will happen automatically if your input is a table Dataset processed in place
(i.e. without a ``table_name`` parameter) or if you save your results in a CARTO table using the ``table_name``
parameter, and only use the resulting table for any further geocoding.

In case you're geocoding local data from a ``DataFrame`` that you plan to re-geocode again, (e.g. because
you're making your work reproducible by saving all the data preparation steps in a notebook),
we advise to save the geocoding results immediately to the same store from when the data is originally taken,
for example:

.. code:: python

    dataframe = pandas.read_csv('my_data')
    dataframe = Geocoding().geocode(dataframe, 'address').data
    dataframe.to_csv('my_data')

As an alternative you can use the ``cached`` option to store geocoding results in a CARTO table
and reuse them in later geocodings. The parameter is the name of the table used to cache the results,
and can be used with dataframe or query datasets.

.. code:: python

    dataframe = pandas.read_csv('my_data')
    dataframe = Geocoding().geocode(dataframe, 'address', cached='my_data').data

If you execute the previous code multiple times it will only spend credits on the first geocoding;
later ones will reuse the results stored in the ``my_data`` table. This will require extra processing
time. If the csv file should ever change, cached results will only be applied to unmodified
records, and new geocoding will be performed only on new or changed records.

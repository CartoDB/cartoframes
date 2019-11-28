Isolines
^^^^^^^^

The ``cartoframes.data.services.Isolines`` class provides `time and distance isolines <https://carto.com/location-data-services/isolines/>`_
using  `CARTO Location Data Services (LDS) <https://carto.com/location-data-services/>`_

This use these functions a CARTO account is required with a geocoding provider and geocoding quota assigned.
Its use will incur in the expense of geocoding credits.
In the case of accounts with soft geocoding limits, additional charges may apply if the monthly quota is exceeded.

Isodistance and Isochrone areas
"""""""""""""""""""""""""""""""

These two operations compute areas that are within a given range (as a travel time or distance) of a central or source point.
Isochrones correspond to the area that can be reached within a given time in seconds from the source point traveling
through the roads network using the specified modality (either walking or by car).
Isodistances are base instead in travel distance as specified in meters.

There are two methods ``isochrones`` and ``isodistances``, both taking the same parameters and returning similar values.

Two of the arguments in these methods are mandatory: the ``source`` and the ``ranges``.

The source is a dataset which contains the points to be taken as the origins of the travel areas.
Separate areas will be computed for each source point.

The ``ranges`` argument is an array of numbers, each of one specifying either a distance in meters
(for isodistances) or a time in seconds (for isochrones). An individual area will be compute for each
source point and range value.

The resulting dataset will include a ``the_geom`` column with the resulting area and a ``data_range``
numeric column with the corresponding range value. Optionally a ``source_id`` column identifying
the source point can be included, which is useful if the source dataset cotains `cartodb_id` identifiers.

The computed polygons represent the whole area reachable within the specified time or distance
from its source point (if the ``is_destination`` option is used, routes are computed *to* the
source points instead).

This implies that the areas corresponding to larger range values will completely include within them
the areas corresponding to smaller range values. If you intend to visualize the resulting areas by representing
them on a map it may be complicated to avoid larger areas obscuring the smaller ones.

For these reason an alternative outcome, better suited for map representation is also provided by using the
``exclusive`` argument; when this is ``True``, exclusive range areas are produced instead of inclusive range areas.
In *exclusive* mode, for each range value, computed polygons will represent the area within an interval of times
(or distances) between the next lower range, if any, as a mininum time/distance, and the maximum value.
In this manner, the produced areas for a given source point do not overlap, each one representing
an exclusive interval of times or distances. In this case an additional ``lower_data_range`` column
will represent the minimun range value in the area. This will be zero in the case of the areas corresponding to the
smaller range value.

Note that computing exclusive areas will require a longer processing time.

Return value
____________

The result is a tuple composed of two named entries: `data` containing the result
areas and ``metadata`` containing additional information.

The ``data`` component is a Dataframe or a Dataset depending on the kind of ``source``
input.  The other, ``metadata``, is a dictionary.

The ``table_name`` argument, when used, forces the result to be saved as a CARTO table.
When this argurment is used an additional argument ``if_exists`` can be used to determine
the behaviour when the table name already exists in the CARTO account. Possible values are:

* ``fail`` (the default) will yield an error if the table exists
* ``replace`` is used to replace existing tables
* ``append`` adds the new data to an existing table

Additional parameters
_____________________

* ``mode`` with possible values ``'car'`` and ``'walk'`` defines the travel mode.
* ``is_destination`` (False/True) indicates that the input points are to be consider destinations for
  the routes used to compute the area, rather than origins.
* ``mode_type`` type of routes computed: ``'shortest'`` (default) or ``'fastests'``.
* ``mode_traffic`` use traffic data to compute routes: ``'disabled'`` (default) or ``'enabled'``.
* ``resolution`` level of detail of the polygons in meters per pixel. Higher resolution may increase the response time of the service.
* ``maxpoints`` Allows to limit the amount of points in the returned polygons. Increasing the number of maxpoints may increase the response time of the service.
* ``quality`` (1/2/3) Allows you to reduce the quality of the polygons in favor of the response time.

Dry run
"""""""

To find out the number of quota credits that will be spent when computing isochrone or isodistances
areas,  pass a ``dry_run=True`` argument:

.. code:: python

    from cartoframes.data.services import Isolines
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    travel = Isolines()

    dataset = Dataset('YOUR_DATA')
    info = travel.isochrones(dataset, ranges=[1800, 3600], dry_run=True).metadata
    print(info.get('required_quota'))

When ``dry_run`` is True no areas will be computed and no quota will be consumed.
The returned dataset (the ``data`` field of the result named tuple) will be ``None``.


Converting between the exclusive and inclusive range representation
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

These methods are handy to convert a table from one of the representations to the other,
so you can use both in your analyses and visualizations without spendit credits for the two of them.

The assume the areas are saved in a table with a ``cartodb_id``, a ``source_id`` referencing
the source points, a ``data_range`` columns for the range values and ``the_geom``, i.e. the
format created by the ``isochrones`` and ``isodistances`` methods from a source with
a ``cartodb_id`` and saved to a table (``table_name``).

.. code:: python

    def inclusive_to_exclusive(inclusive_table_name, exclusive_table_name, if_exists='fail', credentials=None):
        sql = """
            SELECT
                cartodb_id,
                source_id,
                data_range,
                COALESCE(
                    LAG(data_range, 1) OVER (PARTITION BY source_id ORDER BY data_range),
                    0
                ) AS lower_data_range,
                COALESCE(
                    ST_DIFFERENCE(the_geom, LAG(the_geom, 1) OVER (PARTITION BY source_id ORDER BY data_range)),
                    the_geom
                ) AS the_geom
            FROM {table_name}
        """.format(table_name=inclusive_table_name)
        Dataset(sql, credentials=credentials).upload(table_name=exclusive_table_name, if_exists=if_exists)

    def exclusive_to_inclusive(exclusive_table_name, inclusive_table_name, if_exists='fail', credentials=None):
        sql = """
            SELECT
                cartodb_id,
                source_id,
                data_range,
                ST_UNION(the_geom) OVER (PARTITION BY source_id ORDER BY data_range) AS the_geom
            FROM {table_name}
        """.format(table_name=exclusive_table_name)
        Dataset(sql, credentials=credentials).upload(table_name=inclusive_table_name, if_exists=if_exists)

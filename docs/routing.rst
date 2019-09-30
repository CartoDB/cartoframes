Routing Services
================

The ``cartoframes.data.dataservices.Routing`` class provides routing-based analysis operations using  `CARTO Location Data Services (LDS) <https://carto.com/location-data-services/>`_
This process requires you to have a CARTO account with a geocoding provider and geocoding quota assigned, and its use will incur in the expense of geocoding credits.
In the case of accounts with soft geocoding limits, additional charges may apply if the monthly quota is exceeded.

Isodistance and Isochrone areas
-------------------------------

These two operations compute areas that are within a given range (as a travel time or distance) of a central or source point.
Isochrones correspond to the area that can be reached within a given time in seconds from the source point traveling
through the roads network using the specified modality (either walking or by car).
Isodistances are base instead in travel distance as specified in meters.

There are two methods, both taking the same parameters, for each of these operations.

Two of the arguments in these methods are mandatory: the ``source`` and the ``ranges``.

The source is a dataset which contains the points to be taken as the origins of the travel areas.
Separate areas will be computed for each source point.

The ``ranges`` argument is an array of numbers, each of one specifying either a distance in meters
(for isodistances) or a time in seconds (for isochrones). An individual area will be compute for each
source point and range value.

The resulting dataset will include a ``the_geom`` column with the resulting area and a ``data_range``
numeric column with the corresponding range value. Optionally a ``source_id`` column identifying
the source point can be included, which is useful if the source dataset cotains `cartodb_id` identifiers.

By default, the computed polygons represent the whole area reachable within the specified time or distancef
from its source point. This implies that the areas corresponding to larger range values will
completely include within them any other area corresponding to smaller range values.
If you intend to visualize the resulting areas by representing them on a map it may be
complicated to avoid larger areas obscuring the smaller ones.
For these reason an alternative outcome, better suited for map representation
is also provided by using the ``exclusive`` argument; when ``True`` exclusive range areas are
produced instead of inclusive range areas.
In *exclusive* mode it will produce, for each range value, the area within an interval of times or distances between
the next lower range, if any, as a mininum time/distance, and the maximum value.
In this manner, the produced areas for a given sorce point do not overlap, each one represents
an exclusive interval of times or distances. In this case an additional ``lower_data_range`` column
will represent the minimun range value in the area. This will be zero in the case of the areas corresponding to the
smaller range value.

Return value
____________

By default the result areas are returned as a Dataframe or a (local) Dataset depending on the
kind of ``source`` input. This data and a dictionary containing metadata about the result are
returned in a tuple. A named tuple is used with names ``data`` and ``metadata``.

The ``table_name`` argument, when used, forces the result to be saved as a CARTO table.
When this argurment is used an additional argument ``if_exists`` can be used to determine
the behaviour when the table name already exists in the CARTO account. Possible values are:

* ``fail`` (the default) will yield an error if the table exists
* ``replace`` is used to replace existing tables
* ``append`` adds the new data to an existing table

Additional parameters
_____________________

* ``mode`` with possible valus ``'car'`` and ``'walk'`` defines the travel mode.
* ``is_destination`` (False/True) indicates that the input points are to be consider destinations for
  the routes used to compute the area, rather than origins.
* ``mode_type`` type of routes computed: ``'shortest'`` (default) or ``'fastests'``.
* ``mode_traffic`` use traffic data to compute routes: ``'disabled'`` (default) or ``'enabled'``.
* ``resolution`` level of detail of the polygons in meters per pixel. Higher resolution may increase the response time of the service.
* ``maxpoints`` Allows to limit the amount of points in the returned polygons. Increasing the number of maxpoints may increase the response time of the service.
* ``quality`` (1/2/3) Allows you to reduce the quality of the polygons in favor of the response time.

Dry run
-------

To find out the number of quota credits that will be spent when computing isochrone or isodistances
areas,  pass a ``dry_run=True`` argument:

.. code:: python

    from cartoframes.data.services import Routing
    from cartoframes.data import Dataset
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='YOUR_USERNAME',
        api_key='YOUR_APIKEY'
    )
    travel = Routing()

    dataset = Dataset('YOUR_DATA')
    _, info = travel.isochrones(dataset, ranges=[1800, 3600], dry_run=True)
    print(info.get('required_quota'))

When ``dry_run`` is True no areas will be computed and no quota will be consumed.
Ther returned dataset will be ``None``.


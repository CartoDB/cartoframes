
Map Layer Classes[¶](#map-layer-classes "Permalink to this headline")
---------------------------------------------------------------------

_class_ `cartoframes.layer.``BaseMap`(_source='voyager'_, _labels='back'_, _only_labels=False_)

Layer object for adding basemaps to a cartoframes map.

Example

Add a custom basemap to a cartoframes map.

import cartoframes
from cartoframes import BaseMap, Layer
cc = cartoframes.CartoContext(BASEURL, APIKEY)
cc.map(layers=\[BaseMap(source='light', labels='front'),
               Layer('acadia_biodiversity')\])



Parameters:

*   **source** (_str__,_ _optional_) – One of `light` or `dark`. Defaults to `voyager`. Basemaps come from [https://carto.com/location-data-services/basemaps/](https://carto.com/location-data-services/basemaps/)
*   **labels** (_str__,_ _optional_) – One of `back`, `front`, or None. Labels on the front will be above the data layers. Labels on back will be underneath the data layers but on top of the basemap. Setting labels to `None` will only show the basemap.
*   **only_labels** (_bool__,_ _optional_) – Whether to show labels or not.

_class_ `cartoframes.layer.``Layer`(_table_name_, _source=None_, _overwrite=False_, _time=None_, _color=None_, _size=None_, _tooltip=None_, _legend=None_)

A cartoframes Data Layer based on a specific table in user’s CARTO database. This layer class is used for visualizing individual datasets with [CartoContext.map](#context.CartoContext.map)’s layers keyword argument.

Example

import cartoframes
from cartoframes import QueryLayer, styling
cc = cartoframes.CartoContext(BASEURL, APIKEY)
cc.map(layers=\[Layer('fantastic\_sql\_table',
                     size=7,
                     color={'column': 'mr\_fox\_sightings',
                            'scheme': styling.prism(10)})\])



Parameters:

*   **table_name** (_str_) – Name of table in CARTO account
*   **Styling** – See [`QueryLayer`](cartoframes.layer.html#cartoframes.layer.QueryLayer "cartoframes.layer.QueryLayer") for a full list of all arguments arguments for styling this map data layer.
*   **source** (_pandas.DataFrame__,_ _optional_) – Not currently implemented
*   **overwrite** (_bool__,_ _optional_) – Not currently implemented

_class_ `cartoframes.layer.``QueryLayer`(_query_, _time=None_, _color=None_, _size=None_, _tooltip=None_, _legend=None_)

cartoframes data layer based on an arbitrary query to the user’s CARTO database. This layer class is useful for offloading processing to the cloud to do some of the following:

*   Visualizing spatial operations using [PostGIS](http://postgis.net/) and [PostgreSQL](https://www.postgresql.org/), which is the database underlying CARTO
*   Performing arbitrary relational database queries (e.g., complex JOINs in SQL instead of in pandas)
*   Visualizing a subset of the data (e.g., `SELECT * FROM table LIMIT 1000`)

Used in the layers keyword in [CartoContext.map](#context.CartoContext.map).

Example

Underlay a QueryLayer with a complex query below a layer from a table. The QueryLayer is colored by the calculated column `abs_diff`, and points are sized by the column `i_measure`.

import cartoframes
from cartoframes import QueryLayer, styling
cc = cartoframes.CartoContext(BASEURL, APIKEY)
cc.map(layers=\[QueryLayer('''
 WITH i_cte As (
 SELECT
 ST\_Buffer(the\_geom::geography, 500)::geometry As the_geom,
 cartodb_id,
 measure,
 date
 FROM interesting_data
 WHERE date > '2017-04-19'
 )
 SELECT
 i.cartodb\_id, i.the\_geom,
 ST\_Transform(i.the\_geom, 3857) AS the\_geom\_webmercator,
 abs(i.measure - j.measure) AS abs_diff,
 i.measure AS i_measure
 FROM i_cte AS i
 JOIN awesome_data AS j
 ON i.event\_id = j.event\_id
 WHERE j.measure IS NOT NULL
 AND j.date < '2017-04-29'
 ''',
                          color={'column': 'abs_diff',
                                 'scheme': styling.sunsetDark(7)},
                          size='i_measure'),
               Layer('fantastic\_sql\_table')\])



Parameters:

*   **query** (_str_) – Query to expose data on a map layer. At a minimum, a query needs to have the columns cartodb_id, the_geom, and the\_geom\_webmercator for the map to display. Read more about queries in [CARTO’s docs](https://carto.com/docs/tips-and-tricks/geospatial-analysis).
*   **time** (_dict_ _or_ _str__,_ _optional_) –

    Time-based style to apply to layer.

    If time is a `str`, it must be the name of a column which has a data type of datetime or float.

    from cartoframes import QueryLayer
    l = QueryLayer('SELECT * FROM acadia_biodiversity',
                   time='bird\_sighting\_time')

    If time is a `dict`, the following keys are options:

    *   column (str, required): Column for animating map, which must be of type datetime or float.
    *   method (str, optional): Type of aggregation method for operating on [Torque TileCubes](https://github.com/CartoDB/torque). Must be one of `avg`, `sum`, or another [PostgreSQL aggregate functions](https://www.postgresql.org/docs/9.5/static/functions-aggregate.html) with a numeric output. Defaults to `count`.
    *   cumulative (`bool`, optional): Whether to accumulate points over time (`True`) or not (`False`, default)
    *   frames (int, optional): Number of frames in the animation. Defaults to 256.
    *   duration (int, optional): Number of seconds in the animation. Defaults to 30.
    *   trails (int, optional): Number of trails after the incidence of a point. Defaults to 2.

    from cartoframes import Layer
    l = Layer('acadia_biodiversity',
              time={
                  'column': 'bird\_sighting\_time',
                  'cumulative': True,
                  'frames': 128,
                  'duration': 15
              })

*   **color** (_dict_ _or_ _str__,_ _optional_) –

    Color style to apply to map. For example, this can be used to change the color of all geometries in this layer, or to create a graduated color or choropleth map.

    If color is a `str`, there are two options:

    *   A column name to style by to create, for example, a choropleth map if working with polygons. The default classification is quantiles for quantitative data and category for qualitative data.
    *   A hex value or [web color name](https://www.w3.org/TR/css3-color/#svg-color).

    \# color all geometries red (#F00)
    from cartoframes import Layer
    l = Layer('acadia_biodiversity',
              color='red')

    \# color on 'num_eggs' (using defalt color scheme and quantification)
    l = Layer('acadia_biodiversity',
              color='num_eggs')

    If color is a `dict`, the following keys are options, with values described:

    *   column (str): Column used for the basis of styling
    *   scheme (dict, optional): Scheme such as styling.sunset(7) from the [styling module](#module-styling) of cartoframes that exposes [CARTOColors](https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names). Defaults to [mint](#styling.mint) scheme for quantitative data and bold for qualitative data. More control is given by using [styling.scheme](#styling.scheme).

        If you wish to define a custom scheme outside of CARTOColors, it is recommended to use the [styling.custom](#styling.custom) utility function.


    from cartoframes import QueryLayer, styling
    l = QueryLayer('SELECT * FROM acadia_biodiversity',
                   color={
                       'column': 'simpson_index',
                       'scheme': styling.mint(7, bin_method='equal')
                   })

*   **size** (_dict_ _or_ _int__,_ _optional_) –

    Size style to apply to point data.

    If size is an `int`, all points are sized by this value.

    from cartoframes import QueryLayer
    l = QueryLayer('SELECT * FROM acadia_biodiversity',
                   size=7)

    If size is a `str`, this value is interpreted as a column, and the points are sized by the value in this column. The classification method defaults to quantiles, with a min size of 5, and a max size of 5. Use the `dict` input to override these values.

    from cartoframes import Layer
    l = Layer('acadia_biodiversity',
              size='num_eggs')

    If size is a `dict`, the follow keys are options, with values described as:

    *   column (str): Column to base sizing of points on
    *   bin_method (str, optional): Quantification method for dividing data range into bins. Must be one of the methods in `BinMethod` (excluding category).
    *   bins (int, optional): Number of bins to break data into. Defaults to 5.
    *   max (int, optional): Maximum point width (in pixels). Defaults to 25.
    *   min (int, optional): Minimum point width (in pixels). Defaults to 5.

    from cartoframes import Layer
    l = Layer('acadia_biodiversity',
              size={
                  'column': 'num_eggs',
                  'max': 10,
                  'min': 2
              })

*   **tooltip** (_tuple__,_ _optional_) – **Not yet implemented.**
*   **legend** – **Not yet implemented.**

Raises:

*   `CartoException` – If a column name used in any of the styling options is not in the data source in query (or table if using [`Layer`](cartoframes.layer.html#cartoframes.layer.Layer "cartoframes.layer.Layer")).
*   `ValueError` – If styling using a `dict` and a `column` key is not present, or if the data type for a styling option is not supported. This is also raised if styling by a geometry column (i.e., `the_geom` or `the_geom_webmercator`). Futher, this is raised if requesting a time-based map with a data source that has geometries other than points.

# -#- coding: utf-8 -#-
"""
********
Overview
********

Analysis in cartoframes takes two forms:

* **Pipelines**: :obj:`AnalysisTree` pipelines where multiple analyses can be
  listed sequentially off a base data source node (e.g., a
  :obj:`Table` object). This tree is lazily evaluated by applying a
  ``.compute()`` method after it is created. Besides the class
  constructor, analyses can be appended to the tree after it has been
  instantiated. See :obj:`AnalysisTree` for more information. This is modeled
  after Builder analysis workflows, scikit-learn's `PipeLine class
  <http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>`__,
  PySpark's SQL syntax, and directed acyclic graphs.

  A key feature of this data structure is that most analyses, besides accepting
  parameters, can also accept other data sources (:obj:`Table`, :obj:`Query`,
  etc.) as well as other :obj:`AnalysisTrees`.

  Example:

    .. code::

      from cartoframes import AnalysisTree, analyses as ca
      tree = AnalysisTree(
          Table(cc, 'brooklyn_demographics'),
          [
               ('buffer', ca.Buffer(100.0)),
               ('join', ca.Join(
                   Table('gps_pings').filter('type=cell')
                   on='the_geom',
                   type='left',
                   null_replace=0)
               ),
               ('distinct', ca.Distinct(on='user_id')),
               ('agg', ca.Agg(
                   by=['geoid', 'the_geom', ],
                   [('num_gps_pings', 'count'),
                    ('num_gps_pings', 'avg'),
                    ('median_income', 'min')]),
               ('div', ca.Division([
                   ('num_gps_pings', 'total_pop'),
                   ('num_gps_pings', 'the_geom')
               ]))
          ]
      )

* **Method Chaining**: By chaining analysis methods off of a base data source
  node. A base data source can be a supported `Data Source <#data-sources>`__.
  For a full list of analyses, see the methods of :obj:`Query` and
  :obj:`Table`.

  Example:

    .. code::

      from cartoframes import Table
      pt_count = Table('brooklyn_demographics')\\
          .join(Table('gps_pings'), on='the_geom', type='left')\\
          .agg([('num_gps_pings', 'count'), ], by='the_geom')

      # calculate results on a subset of the data
      pt_count.compute(subset=0.1)
      pt_count.map(color='num_gps_pings')


Data Sources
============

The following data sources can be used as nodes:

* :obj:`Table` - a table present in user account
* :obj:`Query` - a query against user account
* :obj:`BuilderAnalysis` - an analysis node already performed
* :obj:`LocalData` - use local data (file, dataframe, etc.)
* :obj:`AnalysisTree` - previously constructed analysis tree

Analysis Library
================

These include traditional GIS operations, common database operations like
JOINs, and more advanced spatial statistics. `Geopandas
<http://geopandas.org/geometric_manipulations.html>`__ has some nice
functionality for operations like this, as does pandas and pyspark. Here we
want to take advantage of CARTO's cloud-based database to perform these
methods, while being careful to stay in a Pythonic syntax like you see in
pandas. Other reference: OGC standards:
http://www.opengeospatial.org/standards/sfs

Functions
---------

- :obj:`AddressNormalization` (#377)
- :obj:`Agg`

  - **Use Case:** Summary info of any category/group
  - Params

    - agg_values (list of agg/column tuples): If `category` is specified, use
      this option for carrying over aggregations within categories. Options
      available are: `min`, `max`, `count`, `avg`, `sum`, `stddev` and other
      `PostgreSQL aggregation operations
      <https://www.postgresql.org/docs/9.6/static/functions-aggregate.html>`__.

- :obj:`Area`

  - Use Case: Add an area column calculated from geometry in square kilometers.
  - Params

    - units (str): One of ``sqkm`` (default), ``sqmeters``, or ``sqmiles``.

- :obj:`Buffer`

  - **Use case:** Buffer points, lines, polygons by a given distance. Used
    widely in spatial analysis for finding points within a distance among
    other uses
  - References

    - `camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/buffer.js>`__

  - Params

    - radius (float, required): radius of buffer in meters

- :obj:`Centroid`

  - References

    - `camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/centroid.js>`__
      but need the ability to carry over summary information: e.g., avg value
      of that centroid group, num of items present
    - Weighted `camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/weighted-centroid.js>`__

  - Params

    - category (str or list of str, optional): Column name(s) to group by.
    - weight (str, optional): weight the centroid based on the weight of a
      column value
    - agg_values (list of agg/column tuples): If `category` is specified, use
      this option for carrying over aggregations within categories. Options
      available are: `min`, `max`, `count`, `avg`, `sum`, `stddev` and other
      `PostgreSQL aggregation operations
      <https://www.postgresql.org/docs/9.6/static/functions-aggregate.html>`__.

- :obj:`Custom`

  - **Use case:** Define a custom analysis using SQL.
  - References

    - `Deprecated SQL node in camshaft
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/deprecated-sql-function.js>`__

  - Params

    - sql (str): Custom analysis defined as a SQL query

- :obj:`DataObs`

  - **Use case:** Augment a dataset with data observatory measures
  - References

    - Existing implementation: `cartoframes docs
      <http://cartoframes.readthedocs.io/en/v0.5.4/#context.CartoContext.data>`__

  - Params

    - same as existing implementation

- :obj:`Difference`
- :obj:`Distinct`

  - **Use case:** De-dupe a dataset on the columns passed
  - Params

    - cols (str or list of str, optional): Column(s) to de-duplicate the
      records on. Default is de-duplicate across all columns. Read more in
      `PostgreSQL documentations
      <https://www.postgresql.org/docs/9.5/static/sql-select.html#SQL-DISTINCT>`__.

  - Example

    .. code::

      Distinct(cols=('the_geom', 'id_num', 'reading'))

- :obj:`Div`

  - **Use case:** Divide one column by another
  - Note: Or should we have an inline-custom function that allows you to write
    select-level math like this. E.g., user can pass ``col1 + 2 * col2 / col3``

  - Params

    - pairs (tuple of str): Tuple of numerator, denominator, and optional name

  - Example

    .. code::

      Div([('num_pings', 'total_pop', 'pings_per_pop'),
           ('num_pings', 'num_unique_foot_traffic'),
           ('num_pings', 1000.0)]

- :obj:`Envelope`

  - **Use Case:** Group geometries into a convex hull, bounding box, bounding
    circle, concave hull, or union
  - References

    - PostGIS docs on these: `convex hull
      <https://postgis.net/docs/ST_ConvexHull.html>`__, `concave hull
      <https://postgis.net/docs/ST_ConcaveHull.html>`__, `bounding box
      <https://postgis.net/docs/ST_Envelope.html>`__, `bounding circle
      <https://postgis.net/docs/ST_MinimumBoundingCircle.html>`__, `union
      <https://postgis.net/docs/ST_Union.html>`__.

  - Params

    - type (str, optional): One of `bounding_box` (default), `convex_hull`,
      `concave_hull`, `bounding_circle`, or `union`
    - category (str or list of str, optional): Column name(s) to group by.
    - agg_values (list of agg/column tuples): If `category` is specified, use
      this option for carrying over aggregations within categories. Options
      available are: `min`, `max`, `count`, `avg`, `sum`, `stddev` and other
      `PostgreSQL aggregation operations
      <https://www.postgresql.org/docs/9.6/static/functions-aggregate.html>`__.

  - Example

    .. code::

      Envelope(type='convex_hull')

- :obj:`FillNull`

  - **Use case:** Fill in null values with a specific value
  - References

    - This uses PostgreSQL's `coalesce
      <https://www.postgresql.org/docs/9.6/static/functions-conditional.html>`__

  - Params

    - fill_vals (dict or list of dicts): Entry in the form:

  - Example

    .. code::

      # option 1
      FillNull({'colname': 1})
      # option 2
      FillNull({'colname': ['other_column', 0]})
      # option 3
      FillNull(
          [{'colname': 1},
           {'colname2': 10},
           {'colname3': ['colname', 'colname2', 0]}])

- :obj:`Filter`

  - **Use case:** Filter out records
  - Params

    - filters (str or list of str): filter (e.g., ``col1 <= 10``) or a list of
      filter conditions. PostgreSQL conditions are valid:
      <https://www.postgresql.org/docs/9.6/static/functions-comparison.html>.

  - Example

    .. code::

      Filter(['col1 <= 10', 'ST_Area(the_geom::geography) > 10'])
      Filter('col1 == col2')

- :obj:`Geocoding`

  - **Use case:** Turn numerical or text data into geometries. E.g., street
    addresses to points, country names to boundaries, IP addresses to points,
    etc.
  - Reference

    - See the files beginning with `georeference` in `camshaft node library
      <https://github.com/CartoDB/camshaft/tree/master/lib/node/nodes>`__

- :obj:`Imputer`

  - **Use case:** Help clean up messy data by filling in null values with the
    mean, median, or mode of the column of interest.
  - Reference

    - Idea comes from `scikit-learn
      <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Imputer.html>`__
    - See also :obj:`StandardScaler`

- :obj:`Isochrone`

  - **Use case:** Drive time polygons, etc.

- :obj:`Join` (spatial or attribute)

  - **Use case:** Combine data from different data sources which have some
    data in common (e.g., points intersecting polygons, JOIN by common column
    values)
  - References

    - `GeoPandas <http://geopandas.org/mergingdata.html>`__
    - `PostgreSQL full list of JOIN types
      <https://www.postgresql.org/docs/9.6/static/queries-table-expressions.html>`__
    - `PySpark
      <http://spark.apache.org/docs/2.1.0/api/python/pyspark.sql.html#pyspark.sql.DataFrame.join>`__

  - Params

    - `on` (str or list of str): column name or list of column names,
      'the_geom' for spatial joins
    - `op` (str): one of `intersects`, `within`, `contains`
    - `how` (str, optional, only use with `on='the_geom'`): `inner`
      (default), `left`, `right`, `outer`, `cross`
    - `expr` (str, optional): Custom expression (e.g., `col1 == col2` a la
      PySpark). TODO: should we use Python's ``==`` syntax or SQL's ``=``
      and then convert internally
    - `agg` (TBD, optional): implicit group by / aggregation

- :obj:`Kmeans`

  - **Use case:** Find clusters in data spatially or in parameter space
  - Reference

    - `camshaft spatial
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/kmeans.js>`__
    - `crankshaft non-spatial
      <https://github.com/CartoDB/crankshaft/blob/develop/doc/11_kmeans.md>`__

- :obj:`Length`

  - **Use case:** Get the length of a linestring in meters, kilometers, or
    miles

- :obj:`Line`

  - **Use case:** Create lines out of a series of points
  - Reference

    - See all `camshaft nodes like line-*
      <https://github.com/CartoDB/camshaft/tree/master/lib/node/nodes>`__

- :obj:`Limit`

  - **Use case:** limit to `n_rows` entries
  - Params:

    - `n_rows` (int): Number of rows to return

- :obj:`MoranLocal`

  - **Use case:** Classify geometries by whether they are in a cluster of
    similarly high or low values, or are an outlier compared to their neighbors
  - References

    - `camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/moran.js>`__
    - `crankshaft functions
      <https://github.com/CartoDB/crankshaft/blob/develop/doc/02_moran.md>`__

  - Params

    - val (str): Column name
    - denom (str, optional): Column name for denominator
    - weight_type (str, optional): one of ``knn`` (default) or ``queen``, which
      requires adjacent geometries
    - n_neighbors (int, optional): Choose the number of neighbors, only valid
      for k-nearest neighbors

- :obj:`Nearest` (give back the n-nearest geometries to another geometry)
- :obj:`NullIf`

  - **Use case:** Replace values with null values if a condition is met. Useful
    for replacing quirky null values like empty strings, values like
    ``'(none)'``, and so on.
  - Params

    - vals (tuple or list of tuples): Column name / value pairs. For example,
      ``('colname', '')`` to replace empty strings in the column `colname` with
      null values.

- :obj:`Routing`

  - **Use case:** Routing
  - References

    - See `camshaft nodes beginning in routing
      <https://github.com/CartoDB/camshaft/tree/master/lib/node/nodes>`__

  - Params

    - destination (tuple of :obj:`Table` or :obj:`Query` and colname)
    - geom_type (str): Whether to return a ``road`` (default) or ``straight``

  - Returns

    - new linestring of route replaces previous `the_geom`
    - length_km (float): length of route
    - duration_sec (float): if possible, return the travel time estimate. Will
      be ``null`` if not possible.

- :obj:`Sample`

  - **Use case:** Sample from a data source
  - References:

    - `camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/sampling.js>`__
      but `TABLESAMPLE` is a better solution
    - `TABLESAMPLE in PostgreSQL
      <https://blog.2ndquadrant.com/tablesample-in-postgresql-9-5-2/>`__.
    - `PySpark sample
      <http://spark.apache.org/docs/2.1.0/api/python/pyspark.sql.html#pyspark.sql.DataFrame.sample>`__
  - Params

    - fraction (float): fraction (0 <= x <= 1) of dataset to return

- :obj:`StandardScaler`

  - **Use case:** Transforms data to be centered on its mean and scaled to have
    unit variance
  - References:

    - Modeled after scikit-learn's `StandardScaler
      <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html#sklearn.preprocessing.StandardScaler>`__

- :obj:`StrJoin` - join a list of column names or literals into a new column

  - **Use case:** Useful for constructing text from a combination of other
    columns and custom values (e.g., a full address from multiple columns).
  - Params

    - vals (list of str): List of columns or literal values to concatenate into
      a new column
    - new_colname (str): New column name


Uncertain about adding
----------------------

- :obj:`Closest`

  - This is a `camshaft node
    <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/closest.js>`__

- :obj:`Contour`

  - Not sure if this is ready for primetime? `camshaft node
    <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/contour.js>`__

- :obj:`Existence`

  - This is a `camshaft node
    <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/filter-by-node-column.js>`__
    related to widgets and connected analysis tables

- :obj:`Gravity`

  - We have a better implementation that's an open PR in crankshaft.

    - `current camshaft node
      <https://github.com/CartoDB/camshaft/blob/master/lib/node/nodes/gravity.js>`__
    - `crankshaft PR <https://github.com/CartoDB/crankshaft/pull/147>`__

.. note::

    * Add status updates (e.g., ``node 5 / 7 complete``)
    * Have a better representation of an analysis? E.g., scikit-learn passes
      class instances to the Pipeline

      .. code::

        from sklearn import svm
        from sklearn.datasets import samples_generator
        from sklearn.feature_selection import SelectKBest, f_regression
        from sklearn.pipeline import Pipeline
        # build pipeline
        anova_filter = SelectKBest(f_regression, k=5)
        clf = svm.SVC(kernel='linear')
        anova_svm = Pipeline([('anova', anova_filter), ('svc', clf)])

      Each 'analysis' in cartoframes could exist as a class and be constructed
      similarly. Most would be a clone of the camshaft node, and others would
      be more data-science-specific.
    * Method chaining builds up an AnalysisTree by reapeatedly applying the
      ``.append(...)`` to ``self``
    * Chained methods are lazily evaluated as well
    * Add AnalysisTree validation steps for column names / existence of data,
      etc. for each step of the tree
    * Instantiating the :obj:`Table` or :obj:`Query` classes is clumsy if the
      ``cc`` needs to be passed to it everytime -- should it be instantiated
      differently? Maybe like ``cc.table('foo')``, which is equivalent to
      ``Table(cc, 'foo')``? One conflict here is that ``cc.query`` already
      exists and means something different.
    * ``Layer`` should have a ``Query`` attribute instead of storing the query
      as a string?
    * Idea: Partial evaluation to get states of the data along the tree? User
      could create a shorter tree to do this instead.
    * Use Python's operator overloading for operations like
      `Analyses + Analysis` does an ``AnalysisTree.append`` under the hood
    * Add method for trashing / invalidating analysis table and starting anew
    * What's the standard on column name inheritance from analysis n to n+1?
      Which columns come over, which don't, and which are added?
    * What can be gleaned from http://www.opengeospatial.org/standards/wps ?
    * Draw inspiration from Spark:
      http://spark.apache.org/docs/2.2.0/api/python/pyspark.sql.html
      And place functions/classes into a `functions` module
      http://spark.apache.org/docs/2.2.0/api/python/pyspark.sql.html#module-pyspark.sql.functions
    * Keep in mind that the chain is actually a tree since data can come in
      at different nodes. AnalysisTree may be a better name.
    * How should the analyses be structured? Similar to scikit-learn's
      PipeLine? `[A(param), B(param)]` and `A(param).fit(data)` happens once
      the tree is evaluated?
    * Ability to mix in analyses that are run locally
    * Standardize aggregation tuples as they appear in many places. Besides
      required values, we could have `distinct`, nullif, coalesce, etc.
      handling options
"""
import pandas as pd
from cartoframes import utils


def _buffer(q_obj, dist):
    """Buffer a query or table"""
    if isinstance(q_obj, Query):
        query = q_obj.query
    else:
        query = q_obj
    return '''
        SELECT
            ST_Buffer(the_geom, {dist}) as the_geom
        FROM (
            {source_query}
        ) as _w
    '''.format(
        dist=dist,
        source_query=query
    )


class AnalysisTree(object):
    """Build up an analysis tree à la Builder Analysis or scikit learn
    Pipeline. Once evaluated with ``AnalysisTree.compute()``, the results will
    persist as a table in the user CARTO account and be returned into the
    ``data`` attribute.

    :obj:`AnalysisTree` allows you to build up a tree of analyses which are
    applied sequentially to a source (:obj:`Query` or :obj:`Table`).

    The analysis inputs can be passed as a list of analyses, or as a list of
    tuples, each with a unique identifier `key` so it can be later referenced
    or removed from the chain programmatically.

    :obj:`AnalysisTree` can also be used as a layer in a map. If it has not
    already been evaluated, then `.compute()` will be applied to it and the map
    will not render until the result is computed.

    Example:

      Build and evaluate an analysis tree, return the results into a
      pandas DataFrame, and map the output

      .. code::

        from cartoframes import AnalysisTree, Table, CartoContext
        from cartoframes import analyses as ca
        cc = CartoContext()

        # base data node
        bklyn_demog = Table(cc, 'brooklyn_demographics')

        # build analysis tree
        tree = AnalysisTree(
            bklyn_demog,
            [
                # buffer by 100 meters
                ca.Buffer(100.0),
                # spatial join
                ca.Join(target=Table(cc, 'gps_pings').filter('type=cell'),
                    on='the_geom',
                    type='left'),
                ca.Distinct(on='user_id'),
                # aggregate points to polygons
                ca.Agg(by='geoid', ops=[('count', 'num_gps_pings'), ]),
                # add new column to normalize point count
                ca.Div([('num_gps_pings', 'total_pop')])
            ]
        )

        # evaluate analysis
        tree.compute()

        # visualize with carto map
        tree.map(color='num_gps_pings_per_total_pop')

    Parameters:

      source (:obj:`str`, :obj:`Table`, or :obj:`Query`): If str, the name of a table
        in user account. If :obj:`Table` or :obj:`Query`, the base data for the
        analysis tree.
      analyses (list): A list of analyses to apply to `source`. The following
        are `available analyses <#functions>`__ and their parameters.

    Attributes:
      - data (pandas.DataFrame): ``None`` until the analysis tree is
        evaluated, and then a dataframe of the results
      - state (:obj:`str`): Current state of the :obj:`AnalysisTree`:

        - 'not evaluated': Chain has not yet been evaluated
        - 'running': Analysis is currently running
        - 'enqueued': Analysis is queued to be run
        - 'complete': Chain successfully run. Results stored in
          :obj:`AnalysisTree.data` and ``.results_url``.
        - 'failed': Failure message if the analysis failed to complete

      - results_url: URL where results stored on CARTO. Note: user has to
        be authenticated to view the table
      - Add method for running the analysis off of a subsample of the data.
        E.g., ``.compute(subsample=0.1)``, ``.compute_preview()``, etc. etc.
        With the goal that users feel compelled to run the analysis first on
        a smaller sample to get the results before running the whole enchilada.
    """ # noqa
    def __init__(self, source, analyses):
        self.context = source.context
        self.analyses = analyses
        self.source = source
        self.data = None
        self.final_query = None

    def _build_tree(self):
        """Builds up an analysis based on `analyses`"""
        temp = 'SELECT * FROM ({query}) as _w{n}'
        last = temp.format(query=self.source.query, n=0)
        for idx, analysis in enumerate(self.analyses):
            last = temp.format(
                query=analysis[0](last, *analysis[1]),
                n=idx+1
            )
        self.final_query = last

    def __repr__(self):
        """.. todo::

            this should pretty print the analyses and parameters
        """
        print(str(self.analyses))

    @property
    def results_url(self):
        """returns the URL where the analysis table exists on CARTO"""
        pass

    def append(self, analysis):
        """Append a new analysis to an existing tree.

        Example:

          .. code::

            tree = AnalysisTree(
                Table('transactions'),
                [
                    Buffer(100),
                    DataObs('median_income')
                ]
            )
            tree.append(('knn', {'mean': 'median_income'}))

        Args:
          analysis (analysis): An analysis node
        """
        pass

    def compute(self, subset=None):
        """Trigger the AnalysisTree to run.

        Example:

          ::

            tree = AnalysisTree(...)
            # compute analysis tree
            tree.compute()
            # show results
            df.data.head()

        Returns:
            promise object, which reports the status of the analysis if not
            complete. Once the analysis finishes, the results will be stored
            in the attributes ``data``, ``results_url``, and ``state``. Also
            returned would be: compute time and other metadata about the job.
        """
        if subset:
            pass
        if self.final_query:
            return self.context.query(self.final_query)
        else:
            raise ValueError('No analysis nodes provided to analysis tree')


class Query(object):
    """:obj:`Query` gives a representation of a query in a users's CARTO
    account.

    Example:

      ::

        from cartoframes import CartoContext, Query
        cc = CartoContext()
        snapshot = Query('''
            SELECT
                count(*) as num_sightings,
                b.acadia_district_name,
                b.the_geom
            FROM
                bird_sightings as a, acadia_districts as b
            WHERE
                ST_Intersects(b.the_geom, a.the_geom)
            GROUP BY 2, 3
        ''')
        snapshot.local_moran('num_sightings', 5).filter('significance<=0.05')


    Parameters:

        context (:obj:`CartoContext`): :obj:`CartoContext` instance
          authenticated against the user's CARTO account.
        query (str): Valid query against user's CARTO account.
    """
    def __init__(self, context, query):
        self.query = query
        self.context = context

    @property
    def columns(self):
        """return the column names of the table or query

        Returns:
          pandas.Index: Column names
        """
        subquery = 'SELECT * FROM ({query}) AS _W LIMIT 0'.format(
            query=self.query)
        cols = self.context.sql_client.send(subquery)
        return pd.Index(cols['fields'].keys())

    @property
    def pgtypes(self):
        """return the dtypes of the columns of the table or query

        Returns:
            pandas.Series: Data types (in a PostgreSQL database) of columns
        """
        subquery = 'SELECT * FROM ({query}) as _w LIMIT 0'.format(
            query=self.query)
        dtypes = self.context.sql_client.send(subquery)
        temp = {k: v['type'] for k, v in utils.dict_items(dtypes['fields'])}
        return pd.Series(temp)

    def _validate_query(self, cols=None):
        """
        Validate that the query has the needed column names for the analysis
        to run
        """
        util_cols = ('cartodb_id', 'the_geom', 'the_geom_webmercator', )
        if cols is None:
            cols = util_cols
        self.context.query(
            # NOTE: would `ANALYZE SELECT {cols} ... be better?
            'SELECT {cols} FROM ({query}) AS _w LIMIT 0'.format(
                cols=','.join(cols),
                query=self.query
            )
        )

    def stop(self):
        """stop job from running. Other names: halt, delete, ...
        This operates on the promise object after running AnalysisTree.compute
        """
    def head(self, n_rows=5):
        """similar to pandas.DataFrame.head"""
        return self.context.query(
            'SELECT * FROM {query} as _w LIMIT {n}'.format(
                query=self.query,
                n=n_rows
            )
        )

    def tail(self, n_rows=5):
        """Return last n_rows of self.query"""
        pass

    def read(self):
        """Read the query to a pandas DataFrame

        Returns:
            pandas.DataFrame: Query represented as a pandas DataFrame
        """
        return self.context.query(self.query)

    def moran_local(self, colname, denom=None, n_neighbors=5):
        """Local Moran's I

        Args:
          colname (:obj:`str`): Column name for performing Local Moran's I
            analysis on
          denom (:obj:`str`, optional): Optional denominator for `colname`.
          n_neighbors (:obj:`int`, optional): Number of neighbors for each
            geometry. Defaults to 5.
        """
        pass

    def div(self, numerator, denominator):
        """Divided one column by another column or expression to produce a new
        column

        Example:

            Divide by a constant to convert from square kilometers to square
            miles.

            ::

                from cartoframes import CartoContext, Table
                cc = CartoContext()
                t = Table(cc, 'acadia_biodiversity')
                t.div('ospreys_per_sqkm', 1.6**2)

            Normalize a column by another column.

            ::

                t = Table(cc, 'acadia_biodiversity')
                t.div('osprey_count', 'num_observations')

            Get the density of a value.

            ::

                t = Table(cc, 'acadia_biodiversity')
                t.div('osprey_count', 'the_geom')
        """
        pass

    def plot(self):
        """Plot all the columns in the query.

        Example:

        ::

            Query('''
                SELECT simpson_index, species
                FROM acadia_biodiversity
            ''').plot()
            <matplotlib plot>

        """
        return self.context.query(self.query).plot()

    def buffer(self, dist):
        """Buffer query

        Example:

            .. code::

                q = Query('...')
                buffered_q = q.buffer(150).compute()
                cc.map(layers=[buffered_q, q])

        Args:
            dist (float): Distance in meters to buffer a geometry
        """
        return Query(self.context, _buffer(self, dist))

    def custom(self, query):
        """Define custom query to add to the tree

        Can info be gleaned from the spark registerUDF?
        http://spark.apache.org/docs/2.1.0/api/python/pyspark.sql.html#pyspark.sql.SQLContext.registerJavaFunction
        """
        pass

    def describe(self, cols=None):
        """Gives back basic statistics for a table

        Args:
          cols (list of str): List of column names to get summary statistics

        Returns:
            pandas.DataFrame: A statistical description of the data

        .. todo: add geometry information
        """
        if cols is None:
            cols = self.context.read(limit=0).columns
        # qualities = ('count', 'avg', 'min', 'max', )
        summary_query = utils.minify_sql((
            'SELECT {aggcols}',
            'FROM ({query}) as _w')).format(
                aggcols=('{agg}({col}) as {col}'.format(agg=None, col=None)),
                query=self.query)
        return self.context.query(summary_query)


class Table(Query):
    """Table object"""
    def __init__(self, context, table_name):
        """Table object"""
        super(Table, self).__init__(
            context,
            'SELECT * FROM {}'.format(table_name)
        )


class BuilderAnalysis(Query):
    """Builder analysis node. Use this option for placing an analysis node
    from Builder."""
    def __init__(self, context, node_hash):
        super(BuilderAnalysis, self).__init__(
            context,
            'select * from {}'.format(node_hash)
        )


class LocalData(Table):
    """Use a local file, dataframe, etc. as a node in the analysis framework"""
    def __init__(self, context, data):
        super(LocalData, self).__init__(
            context,
            data
        )

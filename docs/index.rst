.. cartoframes documentation master file, created by
   sphinx-quickstart on Mon Feb 27 17:03:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

.. toctree::
   :maxdepth: 2

CARTOframes Functionality
=========================

CartoContext
------------
.. autoclass:: context.CartoContext
    :member-order: bysource
    :members: read, query, delete, map, data_discovery, data, data_boundaries

    .. automethod:: write(df, table_name, temp_dir=SYSTEM_TMP_PATH, overwrite=False, lnglat=None, encode_geom=False, geom_col=None, \*\*kwargs)

Map Layer Classes
-----------------
.. automodule:: layer
    :members: BaseMap, Layer, QueryLayer

Map Styling Functions
---------------------
.. automodule:: styling
    :members:
    :member-order: bysource

BatchJobStatus
--------------
.. autoclass:: context.BatchJobStatus
    :members:

Credentials Management
----------------------
.. automodule:: credentials
    :members:

Magic Functions
-----------------
.. method:: %cartoquery [-c CARTOCONTEXT] tablename

  Return results of a query to a CARTO table as a Pandas Dataframe.
  This function can be used both as a line and cell magic.
      - In line mode, you must specify a CARTO table name as a positional
        argument in line. The returned results will be from the query
        `select * from tablename`.
      - In cell mode, you must specify the query in the cell body

      Positional arguments:
          - tablename: a CARTO table name

      Optional arguments:
          - `-c`                An optional argument for specifying a CartoContext
      Returns:
          pandas.DataFrame: DataFrame representation of query on `tablename`
          from CARTO.

      Examples:
          Line magic
          ::
              import cartoframes
              cc = cartoframes.CartoContext(BASEURL, APIKEY)
              %cartoquery -c cc TABLENAME
          Cell magic
          ::
              import cartoframes
              creds = cartoframes.Credentials(username='eschbacher', key='abcdefg')
              eschbacher_cc = cartoframes.CartoContext(creds=creds)
              %%cartoquery -cc eschbacher_cc
              SELECT cartodb_id, the_geom from TABLENAME
              LIMIT 2

.. method:: %cartomap [-c CARTOCONTEXT -s STYLECOL -t TIMECOL -i -v] tablename

    Return results of a query as a CARTO map.
    This function can be used both as a line and cell magic.
        - In line mode, you must specify a CARTO table name as a positional
          argument in line. The returned mapped results will be from the query
          `select * from tablename`.
        - In cell mode, you must specify the query in the cell body. The query
          must return the column `the_geom_webmercator`

    Positional arguments:
        - tablename:        a CARTO table name

    Optional arguments:

    - `-c`               An optional argument for specifying a CartoContext.
    - `-i`               Specify an interactive map; otherwise returns a static map
    - `-s`               Specifying a column by which to apply an autostyle
    - `-t`               Specify a time column to apply a time animated styling
    - `-v`               Print verbose code that generated map


    Returns:
        IPython.display.HTML or matplotlib Axes: Interactive maps are
        rendered as HTML in an `iframe`, while static maps are returned as
        matplotlib Axes objects or IPython Image.

    Line magic
    ::
      import cartoframes
      cc = cartoframes.CartoContext(BASEURL, APIKEY)
      %cartomap -c cc my_table

    Cell magic
    ::
      import cartoframes
      cc = cartoframes.CartoContext()
      %%cartoquery
      SELECT * from my_table
      WHERE field_1 > 3

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

:Version: |version|

.. automodule:: cartoframes.context


CartoContext
============
.. autoclass:: cartoframes.context.CartoContext
    :noindex:
    :member-order: bysource
    :members: read, query, delete, map, data_discovery, data, data_boundaries

    .. automethod:: write(df, table_name, temp_dir=SYSTEM_TMP_PATH, overwrite=False, lnglat=None, encode_geom=False, geom_col=None, \*\*kwargs)
    .. automethod:: tables()

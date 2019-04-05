class Basemap(object):  # pylint: disable=too-few-public-methods
    """Supported CARTO vector basemaps. Read more about the styles in the
    `CARTO Basemaps repository <https://github.com/CartoDB/basemap-styles>`__.

    Attributes:
        darkmatter (str): CARTO's "Dark Matter" style basemap
        positron (str): CARTO's "Positron" style basemap
        voyager (str): CARTO's "Voyager" style basemap

    Example:
        Create an embedded map using CARTO's Positron style with no data layers

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext()
            vector.vmap([], context=cc, basemap=vector.Basemaps.positron)
    """
    positron = 'Positron'
    darkmatter = 'DarkMatter'
    voyager = 'Voyager'

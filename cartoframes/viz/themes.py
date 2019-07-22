class Themes(object):  # pylint: disable=too-few-public-methods
    """UI color theme applied to Widgets and Legends.
    When selecting the DarkMatter basemap, the Dark theme is used by default.

    Attributes:
        dark (str)
        light (str)

    Example:
        Create an embedded map using CARTO's Positron style with the dark theme

        .. code::

            from cartoframes.viz import Map, basemaps, themes

            Map(basemap=basemaps.positron, theme=themes.dark)
    """
    dark = 'dark'
    light = 'light'

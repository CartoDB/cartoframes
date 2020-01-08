class Themes:  # pylint: disable=too-few-public-methods
    """UI color theme applied to Widgets and Legends.
    When selecting the DarkMatter basemap, the Dark theme is used by default.

    Example:
        Create an embedded map using CARTO's Positron style with the dark theme

        >>> Map(theme=themes.dark)

    """
    dark = 'dark'
    light = 'light'

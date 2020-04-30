class Palettes:  # pylint: disable=too-few-public-methods
    """Color palettes applied to Map visualizations in the style helper methods.
    By default, each color helper method has its own default palette.
    More information at https://carto.com/carto-colors/

    Example:
        Create color bins style with the burg palette

        >>> color_bins_style('column name', palette=palettes.burg)

    """
    pass


PALETTES = [
    'BURG',
    'BURGYL',
    'REDOR',
    'ORYEL',
    'PEACH',
    'PINKYL',
    'MINT',
    'BLUGRN',
    'DARKMINT',
    'EMRLD',
    'AG_GRNYL',
    'BLUYL',
    'TEAL',
    'TEALGRN',
    'PURP',
    'PURPOR',
    'SUNSET',
    'MAGENTA',
    'SUNSETDARK',
    'AG_SUNSET',
    'BRWNYL',
    'ARMYROSE',
    'FALL',
    'GEYSER',
    'TEMPS',
    'TEALROSE',
    'TROPIC',
    'EARTH',
    'ANTIQUE',
    'BOLD',
    'PASTEL',
    'PRISM',
    'SAFE',
    'VIVID'
    'CB_YLGN',
    'CB_YLGNBU',
    'CB_GNBU',
    'CB_BUGN',
    'CB_PUBUGN',
    'CB_PUBU',
    'CB_BUPU',
    'CB_RDPU',
    'CB_PURD',
    'CB_ORRD',
    'CB_YLORRD',
    'CB_YLORBR',
    'CB_PURPLES',
    'CB_BLUES',
    'CB_GREENS',
    'CB_ORANGES',
    'CB_REDS',
    'CB_GREYS',
    'CB_PUOR',
    'CB_BRBG',
    'CB_PRGN',
    'CB_PIYG',
    'CB_RDBU',
    'CB_RDGY',
    'CB_RDYLBU',
    'CB_SPECTRAL',
    'CB_RDYLGN',
    'CB_ACCENT',
    'CB_DARK2',
    'CB_PAIRED',
    'CB_PASTEL1',
    'CB_PASTEL2',
    'CB_SET1',
    'CB_SET2',
    'CB_SET3'
]

for palette in PALETTES:
    setattr(Palettes, palette.lower(), palette)

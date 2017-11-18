"""Styling module that exposes CARTOColor schemes. Read more about CARTOColor
in its `GitHub repository <https://github.com/Carto-color/>`__.

.. image:: https://cloud.githubusercontent.com/assets/1566273/21021002/fc9df60e-bd33-11e6-9438-d67951a7a9bf.png
    :width: 700px
    :alt: CARTOColors
"""  # noqa


class BinMethod:
    """Data classification methods used for the styling of data on maps.

    Attributes:
        quantiles (str): Quantiles classification for quantitative data
        jenks (str): Jenks classification for quantitative data
        headtails (str): Head/Tails classification for quantitative data
        equal (str): Equal Interval classification for quantitative data
        category (str): Category classification for qualitative data
    """
    quantiles = 'quantiles'
    jenks = 'jenks'
    headtails = 'headtails'
    equal = 'equal'
    category = 'category'


def get_scheme_cartocss(column, scheme_info):
    """Get TurboCARTO CartoCSS based on input parameters"""
    if 'colors' in scheme_info:
        color_scheme = '({})'.format(','.join(scheme_info['colors']))
    else:
        color_scheme = 'cartocolor({})'.format(scheme_info['name'])
    bin_method = scheme_info['bin_method']
    return ('ramp([{column}], {color_scheme}, '
            '{bin_method}({bins}){comparison})').format(
                column=column,
                color_scheme=color_scheme,
                bin_method=bin_method,
                bins=scheme_info['bins'],
                comparison=('' if bin_method == 'category' else ', <=')
            )


def custom(colors, bins=None, bin_method=BinMethod.quantiles):
    """Create a custom scheme.

    Args:
        colors (list of str): List of hex values for styling data
        bins (int, optional): Number of bins to style by. If not given, the
          number of colors will be used.
        bin_method (str, optional): Classification method. One of the values
          in :obj:`BinMethod`. Defaults to `quantiles`, which only works with
          quantitative data.
    """
    return {
        'colors': colors,
        'bins': bins if bins is not None else len(colors),
        'bin_method': bin_method,
    }


def scheme(name, bins, bin_method):
    """Return a custom scheme based on CARTOColors.

    Args:
        name (str): Name of a CARTOColor.
        bins (int): Number of bins for classifying data. CARTOColors have 7
          bins max for quantitative data, and 11 max for qualitative data.
        bin_method (str): One of methods in :obj:`BinMethod`.

    .. Warning::

       Input types are particularly sensitive in this function, and little
       feedback is given for errors. ``name`` and ``bin_method`` arguments
       are case-sensitive.

    """
    return {
        'name': name,
        'bins': bins,
        'bin_method': bin_method,
    }


# Get methods for CARTOColor schemes
def burg(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Burg quantitative scheme"""
    return scheme('Burg', bins, bin_method)


def burgYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColor BurgYl quantitative scheme"""
    return scheme('BurgYl', bins, bin_method)


def redOr(bins, bin_method=BinMethod.quantiles):
    """CARTOColor RedOr quantitative scheme"""
    return scheme('RedOr', bins, bin_method)


def orYel(bins, bin_method=BinMethod.quantiles):
    """CARTOColor OrYel quantitative scheme"""
    return scheme('OrYel', bins, bin_method)


def peach(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Peach quantitative scheme"""
    return scheme('Peach', bins, bin_method)


def pinkYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColor PinkYl quantitative scheme"""
    return scheme('PinkYl', bins, bin_method)


def mint(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Mint quantitative scheme"""
    return scheme('Mint', bins, bin_method)


def bluGrn(bins, bin_method=BinMethod.quantiles):
    """CARTOColor BluGrn quantitative scheme"""
    return scheme('BluGrn', bins, bin_method)


def darkMint(bins, bin_method=BinMethod.quantiles):
    """CARTOColor DarkMint quantitative scheme"""
    return scheme('DarkMint', bins, bin_method)


def emrld(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Emrld quantitative scheme"""
    return scheme('Emrld', bins, bin_method)


def bluYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColor BluYl quantitative scheme"""
    return scheme('BluYl', bins, bin_method)


def teal(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Teal quantitative scheme"""
    return scheme('Teal', bins, bin_method)


def tealGrn(bins, bin_method=BinMethod.quantiles):
    """CARTOColor TealGrn quantitative scheme"""
    return scheme('TealGrn', bins, bin_method)


def purp(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Purp quantitative scheme"""
    return scheme('Purp', bins, bin_method)


def purpOr(bins, bin_method=BinMethod.quantiles):
    """CARTOColor PurpOr quantitative scheme"""
    return scheme('PurpOr', bins, bin_method)


def sunset(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Sunset quantitative scheme"""
    return scheme('Sunset', bins, bin_method)


def magenta(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Magenta quantitative scheme"""
    return scheme('Magenta', bins, bin_method)


def sunsetDark(bins, bin_method=BinMethod.quantiles):
    """CARTOColor SunsetDark quantitative scheme"""
    return scheme('SunsetDark', bins, bin_method)


def brwnYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColor BrwnYl quantitative scheme"""
    return scheme('BrwnYl', bins, bin_method)


def armyRose(bins, bin_method=BinMethod.quantiles):
    """CARTOColor ArmyRose divergent quantitative scheme"""
    return scheme('ArmyRose', bins, bin_method)


def fall(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Fall divergent quantitative scheme"""
    return scheme('Fall', bins, bin_method)


def geyser(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Geyser divergent quantitative scheme"""
    return scheme('Geyser', bins, bin_method)


def temps(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Temps divergent quantitative scheme"""
    return scheme('Temps', bins, bin_method)


def tealRose(bins, bin_method=BinMethod.quantiles):
    """CARTOColor TealRose divergent quantitative scheme"""
    return scheme('TealRose', bins, bin_method)


def tropic(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Tropic divergent quantitative scheme"""
    return scheme('Tropic', bins, bin_method)


def earth(bins, bin_method=BinMethod.quantiles):
    """CARTOColor Earth divergent quantitative scheme"""
    return scheme('Earth', bins, bin_method)


def antique(bins, bin_method=BinMethod.category):
    """CARTOColor Antique qualitative scheme"""
    return scheme('Antique', bins, bin_method)


def bold(bins, bin_method=BinMethod.category):
    """CARTOColor Bold qualitative scheme"""
    return scheme('Bold', bins, bin_method)


def pastel(bins, bin_method=BinMethod.category):
    """CARTOColor Pastel qualitative scheme"""
    return scheme('Pastel', bins, bin_method)


def prism(bins, bin_method=BinMethod.category):
    """CARTOColor Prism qualitative scheme"""
    return scheme('Prism', bins, bin_method)


def safe(bins, bin_method=BinMethod.category):
    """CARTOColor Safe qualitative scheme"""
    return scheme('Safe', bins, bin_method)


def vivid(bins, bin_method=BinMethod.category):
    """CARTOColor Vivid qualitative scheme"""
    return scheme('Vivid', bins, bin_method)

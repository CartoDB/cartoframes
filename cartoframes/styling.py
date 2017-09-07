"""Styling module that exposes CartoColor schemes. Read more about CartoColor
in its `GitHub repository <https://github.com/Carto-color/>`__.

.. image:: https://cloud.githubusercontent.com/assets/1566273/21021002/fc9df60e-bd33-11e6-9438-d67951a7a9bf.png
    :width: 700px
    :alt: CartoColors
"""


class BinMethod:
    quantiles = 'quantiles'
    jenks = 'jenks'
    headtails = 'headtails'
    equal = 'equal'
    category = 'category'


def get_scheme_cartocss(column, scheme_info):
    """Get TurboCartoCSS based on input parameters"""
    if 'colors' in scheme_info:
        color_scheme = '({})'.format(','.join(scheme_info['colors']))
    else:
        color_scheme = 'cartocolor({})'.format(scheme_info['name'])

    return "ramp([{column}], {color_scheme}, {bin_method}({bins}))".format(
        column=column,
        color_scheme=color_scheme,
        bin_method=scheme_info['bin_method'],
        bins=scheme_info['bins'],
    )


def custom(colors, bins=None, bin_method=BinMethod.quantiles):
    """Get custom scheme"""
    return {
        'colors': colors,
        'bins': bins if bins is not None else len(colors),
        'bin_method': bin_method,
    }


def _scheme(name, bins, bin_method):
    return {
        'name': name,
        'bins': bins,
        'bin_method': bin_method,
    }


# Get methods for CartoColor schemes
def burg(bins, bin_method=BinMethod.quantiles):
    """CartoColor Burg quantitative scheme
    """
    return _scheme('Burg', bins, bin_method)


def burgYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BurgYl quantitative scheme
    """
    return _scheme('BurgYl', bins, bin_method)


def redOr(bins, bin_method=BinMethod.quantiles):
    """CartoColor RedOr quantitative scheme
    """
    return _scheme('RedOr', bins, bin_method)


def orYel(bins, bin_method=BinMethod.quantiles):
    """CartoColor OrYel quantitative scheme
    """
    return _scheme('OrYel', bins, bin_method)


def peach(bins, bin_method=BinMethod.quantiles):
    """CartoColor Peach quantitative scheme
    """
    return _scheme('Peach', bins, bin_method)


def pinkYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor PinkYl quantitative scheme
    """
    return _scheme('PinkYl', bins, bin_method)


def mint(bins, bin_method=BinMethod.quantiles):
    """CartoColor Mint quantitative scheme
    """
    return _scheme('Mint', bins, bin_method)


def bluGrn(bins, bin_method=BinMethod.quantiles):
    """CartoColor BluGrn quantitative scheme
    """
    return _scheme('BluGrn', bins, bin_method)


def darkMint(bins, bin_method=BinMethod.quantiles):
    """CartoColor DarkMint quantitative scheme
    """
    return _scheme('DarkMint', bins, bin_method)


def emrld(bins, bin_method=BinMethod.quantiles):
    """CartoColor Emrld quantitative scheme
    """
    return _scheme('Emrld', bins, bin_method)


def bluYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BluYl quantitative scheme
    """
    return _scheme('BluYl', bins, bin_method)


def teal(bins, bin_method=BinMethod.quantiles):
    """CartoColor Teal quantitative scheme
    """
    return _scheme('Teal', bins, bin_method)


def tealGrn(bins, bin_method=BinMethod.quantiles):
    """CartoColor TealGrn quantitative scheme
    """
    return _scheme('TealGrn', bins, bin_method)


def purp(bins, bin_method=BinMethod.quantiles):
    """CartoColor Purp quantitative scheme
    """
    return _scheme('Purp', bins, bin_method)


def purpOr(bins, bin_method=BinMethod.quantiles):
    """CartoColor PurpOr quantitative scheme
    """
    return _scheme('PurpOr', bins, bin_method)


def sunset(bins, bin_method=BinMethod.quantiles):
    """CartoColor Sunset quantitative scheme
    """
    return _scheme('Sunset', bins, bin_method)


def magenta(bins, bin_method=BinMethod.quantiles):
    """CartoColor Magenta quantitative scheme
    """
    return _scheme('Magenta', bins, bin_method)


def sunsetDark(bins, bin_method=BinMethod.quantiles):
    """CartoColor SunsetDark quantitative scheme
    """
    return _scheme('SunsetDark', bins, bin_method)


def brwnYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BrwnYl quantitative scheme
    """
    return _scheme('BrwnYl', bins, bin_method)


def armyRose(bins, bin_method=BinMethod.quantiles):
    """CartoColor ArmyRose divergent quantitative scheme
    """
    return _scheme('ArmyRose', bins, bin_method)


def fall(bins, bin_method=BinMethod.quantiles):
    """CartoColor Fall divergent quantitative scheme
    """
    return _scheme('Fall', bins, bin_method)


def geyser(bins, bin_method=BinMethod.quantiles):
    """CartoColor Geyser divergent quantitative scheme
    """
    return _scheme('Geyser', bins, bin_method)


def temps(bins, bin_method=BinMethod.quantiles):
    """CartoColor Temps divergent quantitative scheme
    """
    return _scheme('Temps', bins, bin_method)


def tealRose(bins, bin_method=BinMethod.quantiles):
    """CartoColor TealRose divergent quantitative scheme
    """
    return _scheme('TealRose', bins, bin_method)


def tropic(bins, bin_method=BinMethod.quantiles):
    """CartoColor Tropic divergent quantitative scheme
    """
    return _scheme('Tropic', bins, bin_method)


def earth(bins, bin_method=BinMethod.quantiles):
    """CartoColor Earth divergent quantitative scheme
    """
    return _scheme('Earth', bins, bin_method)


def antique(bins, bin_method=BinMethod.category):
    """CartoColor Antique qualitative scheme
    """
    return _scheme('Antique', bins, bin_method)


def bold(bins, bin_method=BinMethod.category):
    """CartoColor Bold qualitative scheme
    """
    return _scheme('Bold', bins, bin_method)


def pastel(bins, bin_method=BinMethod.category):
    """CartoColor Pastel qualitative scheme
    """
    return _scheme('Pastel', bins, bin_method)


def prism(bins, bin_method=BinMethod.category):
    """CartoColor Prism qualitative scheme
    """
    return _scheme('Prism', bins, bin_method)


def safe(bins, bin_method=BinMethod.category):
    """CartoColor Safe qualitative scheme
    """
    return _scheme('Safe', bins, bin_method)


def vivid(bins, bin_method=BinMethod.category):
    """CartoColor Vivid qualitative scheme
    """
    return _scheme('Vivid', bins, bin_method)

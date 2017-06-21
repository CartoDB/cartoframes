"""Styling module that exposes CartoColor schemes. Read more about CartoColor in its `GitHub repository <https://github.com/Carto-color/>`__.

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

    .. image:: ./img/cartocolor/Burg.png 
    """
    return _scheme('Burg', bins, bin_method)


def burgYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BurgYl quantitative scheme

    .. image:: ./img/cartocolor/BurgYl.png
    """
    return _scheme('BurgYl', bins, bin_method)


def redOr(bins, bin_method=BinMethod.quantiles):
    """CartoColor RedOr quantitative scheme

    .. image:: ./img/cartocolor/RedOr.png
    """
    return _scheme('RedOr', bins, bin_method)


def orYel(bins, bin_method=BinMethod.quantiles):
    """CartoColor OrYel quantitative scheme

    .. image:: ./img/cartocolor/OrYel.png
    """
    return _scheme('OrYel', bins, bin_method)


def peach(bins, bin_method=BinMethod.quantiles):
    """CartoColor Peach quantitative scheme

    .. image:: ./img/cartocolor/Peach.png
    """
    return _scheme('Peach', bins, bin_method)


def pinkYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor PinkYl quantitative scheme

    .. image:: ./img/cartocolor/PinkYl.png
    """
    return _scheme('PinkYl', bins, bin_method)


def mint(bins, bin_method=BinMethod.quantiles):
    """CartoColor Mint quantitative scheme

    .. image:: ./img/cartocolor/Mint.png
    """
    return _scheme('Mint', bins, bin_method)


def bluGrn(bins, bin_method=BinMethod.quantiles):
    """CartoColor BluGrn quantitative scheme

    .. image:: ./img/cartocolor/BluGrn.png
    """
    return _scheme('BluGrn', bins, bin_method)


def darkMint(bins, bin_method=BinMethod.quantiles):
    """CartoColor DarkMint quantitative scheme

    .. image:: ./img/cartocolor/DarkMint.png
    """
    return _scheme('DarkMint', bins, bin_method)


def emrld(bins, bin_method=BinMethod.quantiles):
    """CartoColor Emrld quantitative scheme

    .. image:: ./img/cartocolor/Emrld.png
    """
    return _scheme('Emrld', bins, bin_method)


def bluYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BluYl quantitative scheme

    .. image:: ./img/cartocolor/BluYl.png
    """
    return _scheme('BluYl', bins, bin_method)


def teal(bins, bin_method=BinMethod.quantiles):
    """CartoColor Teal quantitative scheme

    .. image:: ./img/cartocolor/Teal.png
    """
    return _scheme('Teal', bins, bin_method)


def tealGrn(bins, bin_method=BinMethod.quantiles):
    """CartoColor TealGrn quantitative scheme

    .. image:: ./img/cartocolor/TealGrn.png
    """
    return _scheme('TealGrn', bins, bin_method)


def purp(bins, bin_method=BinMethod.quantiles):
    """CartoColor Purp quantitative scheme

    .. image:: ./img/cartocolor/Purp.png
    """
    return _scheme('Purp', bins, bin_method)


def purpOr(bins, bin_method=BinMethod.quantiles):
    """CartoColor PurpOr quantitative scheme

    .. image:: ./img/cartocolor/PurpOr.png
    """
    return _scheme('PurpOr', bins, bin_method)


def sunset(bins, bin_method=BinMethod.quantiles):
    """CartoColor Sunset quantitative scheme

    .. image:: ./img/cartocolor/Sunset.png
    """
    return _scheme('Sunset', bins, bin_method)


def magenta(bins, bin_method=BinMethod.quantiles):
    """CartoColor Magenta quantitative scheme

    .. image:: ./img/cartocolor/Magenta.png
    """
    return _scheme('Magenta', bins, bin_method)


def sunsetDark(bins, bin_method=BinMethod.quantiles):
    """CartoColor SunsetDark quantitative scheme

    .. image:: ./img/cartocolor/SunsetDark.png
    """
    return _scheme('SunsetDark', bins, bin_method)


def brwnYl(bins, bin_method=BinMethod.quantiles):
    """CartoColor BrwnYl quantitative scheme

    .. image:: ./img/cartocolor/BrwnYl.png
    """
    return _scheme('BrwnYl', bins, bin_method)


def armyRose(bins, bin_method=BinMethod.quantiles):
    """CartoColor ArmyRose divergent quantitative scheme

    .. image:: ./img/cartocolor/ArmyRose.png
    """
    return _scheme('ArmyRose', bins, bin_method)


def fall(bins, bin_method=BinMethod.quantiles):
    """CartoColor Fall divergent quantitative scheme

    .. image:: ./img/cartocolor/Fall.png
    """
    return _scheme('Fall', bins, bin_method)


def geyser(bins, bin_method=BinMethod.quantiles):
    """CartoColor Geyser divergent quantitative scheme

    .. image:: ./img/cartocolor/Geyser.png
    """
    return _scheme('Geyser', bins, bin_method)


def temps(bins, bin_method=BinMethod.quantiles):
    """CartoColor Temps divergent quantitative scheme

    .. image:: ./img/cartocolor/Temps.png
    """
    return _scheme('Temps', bins, bin_method)


def tealRose(bins, bin_method=BinMethod.quantiles):
    """CartoColor TealRose divergent quantitative scheme

    .. image:: ./img/cartocolor/TealRose.png
    """
    return _scheme('TealRose', bins, bin_method)


def tropic(bins, bin_method=BinMethod.quantiles):
    """CartoColor Tropic divergent quantitative scheme

    .. image:: ./img/cartocolor/Tropic.png
    """
    return _scheme('Tropic', bins, bin_method)


def earth(bins, bin_method=BinMethod.quantiles):
    """CartoColor Earth divergent quantitative scheme

    .. image:: ./img/cartocolor/Earth.png
    """
    return _scheme('Earth', bins, bin_method)


def antique(bins, bin_method=BinMethod.category):
    """CartoColor Antique qualitative scheme

    .. image:: ./img/cartocolor/Antique.png
    """
    return _scheme('Antique', bins, bin_method)


def bold(bins, bin_method=BinMethod.category):
    """CartoColor Bold qualitative scheme

    .. image:: ./img/cartocolor/Bold.png
    """
    return _scheme('Bold', bins, bin_method)


def pastel(bins, bin_method=BinMethod.category):
    """CartoColor Pastel qualitative scheme

    .. image:: ./img/cartocolor/Pastel.png
    """
    return _scheme('Pastel', bins, bin_method)


def prism(bins, bin_method=BinMethod.category):
    """CartoColor Prism qualitative scheme

    .. image:: ./img/cartocolor/Prism.png
    """
    return _scheme('Prism', bins, bin_method)


def safe(bins, bin_method=BinMethod.category):
    """CartoColor Safe qualitative scheme

    .. image:: ./img/cartocolor/Safe.png
    """
    return _scheme('Safe', bins, bin_method)


def vivid(bins, bin_method=BinMethod.category):
    """CartoColor Vivid qualitative scheme

    .. image:: ./img/cartocolor/Vivid.png
    """
    return _scheme('Vivid', bins, bin_method)

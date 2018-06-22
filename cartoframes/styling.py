"""Styling module that exposes CARTOColors schemes. Read more about CARTOColors
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
        mapping (dict): The TurboCarto mappings
    """
    quantiles = 'quantiles'
    jenks = 'jenks'
    headtails = 'headtails'
    equal = 'equal'
    category = 'category'

    # Mappings: https://github.com/CartoDB/turbo-carto/#mappings-default-values
    mapping = {
        quantiles: '>',
        jenks: '>',
        headtails: '<',
        equal: '>',
        category: '=',
    }


def get_scheme_cartocss(column, scheme_info):
    """Get TurboCARTO CartoCSS based on input parameters"""
    if 'colors' in scheme_info:
        color_scheme = '({})'.format(','.join(scheme_info['colors']))
    else:
        color_scheme = 'cartocolor({})'.format(scheme_info['name'])
    if not isinstance(scheme_info['bins'], int):
        bins = ','.join(str(i) for i in scheme_info['bins'])
    else:
        bins = scheme_info['bins']
    bin_method = scheme_info['bin_method']
    comparison = ', {}'.format(BinMethod.mapping.get(bin_method, '>='))
    return ('ramp([{column}], {color_scheme}, '
            '{bin_method}({bins}){comparison})').format(
                column=column,
                color_scheme=color_scheme,
                bin_method=bin_method,
                bins=bins,
                comparison=comparison)


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


def scheme(name, bins, bin_method='quantiles'):
    """Return a custom scheme based on CARTOColors.

    Args:
        name (str): Name of a CARTOColor.
        bins (int or iterable): If an `int`, the number of bins for classifying
          data. CARTOColors have 7 bins max for quantitative data, and 11 max
          for qualitative data. If `bins` is a `list`, it is the upper range
          for classifying data. E.g., `bins` can be of the form ``(10, 20, 30,
          40, 50)``.
        bin_method (str, optional): One of methods in :obj:`BinMethod`.
          Defaults to ``quantiles``. If `bins` is an interable, then that is
          the bin method that will be used and this will be ignored.

    .. Warning::

       Input types are particularly sensitive in this function, and little
       feedback is given for errors. ``name`` and ``bin_method`` arguments
       are case-sensitive.

    """
    return {
        'name': name,
        'bins': bins,
        'bin_method': (bin_method if isinstance(bins, int) else ''),
    }


# Get methods for CARTOColors schemes
def burg(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Burg quantitative scheme"""
    return scheme('Burg', bins, bin_method)


def burgYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColors BurgYl quantitative scheme"""
    return scheme('BurgYl', bins, bin_method)


def redOr(bins, bin_method=BinMethod.quantiles):
    """CARTOColors RedOr quantitative scheme"""
    return scheme('RedOr', bins, bin_method)


def orYel(bins, bin_method=BinMethod.quantiles):
    """CARTOColors OrYel quantitative scheme"""
    return scheme('OrYel', bins, bin_method)


def peach(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Peach quantitative scheme"""
    return scheme('Peach', bins, bin_method)


def pinkYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColors PinkYl quantitative scheme"""
    return scheme('PinkYl', bins, bin_method)


def mint(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Mint quantitative scheme"""
    return scheme('Mint', bins, bin_method)


def bluGrn(bins, bin_method=BinMethod.quantiles):
    """CARTOColors BluGrn quantitative scheme"""
    return scheme('BluGrn', bins, bin_method)


def darkMint(bins, bin_method=BinMethod.quantiles):
    """CARTOColors DarkMint quantitative scheme"""
    return scheme('DarkMint', bins, bin_method)


def emrld(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Emrld quantitative scheme"""
    return scheme('Emrld', bins, bin_method)


def bluYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColors BluYl quantitative scheme"""
    return scheme('BluYl', bins, bin_method)


def teal(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Teal quantitative scheme"""
    return scheme('Teal', bins, bin_method)


def tealGrn(bins, bin_method=BinMethod.quantiles):
    """CARTOColors TealGrn quantitative scheme"""
    return scheme('TealGrn', bins, bin_method)


def purp(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Purp quantitative scheme"""
    return scheme('Purp', bins, bin_method)


def purpOr(bins, bin_method=BinMethod.quantiles):
    """CARTOColors PurpOr quantitative scheme"""
    return scheme('PurpOr', bins, bin_method)


def sunset(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Sunset quantitative scheme"""
    return scheme('Sunset', bins, bin_method)


def magenta(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Magenta quantitative scheme"""
    return scheme('Magenta', bins, bin_method)


def sunsetDark(bins, bin_method=BinMethod.quantiles):
    """CARTOColors SunsetDark quantitative scheme"""
    return scheme('SunsetDark', bins, bin_method)


def brwnYl(bins, bin_method=BinMethod.quantiles):
    """CARTOColors BrwnYl quantitative scheme"""
    return scheme('BrwnYl', bins, bin_method)


def armyRose(bins, bin_method=BinMethod.quantiles):
    """CARTOColors ArmyRose divergent quantitative scheme"""
    return scheme('ArmyRose', bins, bin_method)


def fall(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Fall divergent quantitative scheme"""
    return scheme('Fall', bins, bin_method)


def geyser(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Geyser divergent quantitative scheme"""
    return scheme('Geyser', bins, bin_method)


def temps(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Temps divergent quantitative scheme"""
    return scheme('Temps', bins, bin_method)


def tealRose(bins, bin_method=BinMethod.quantiles):
    """CARTOColors TealRose divergent quantitative scheme"""
    return scheme('TealRose', bins, bin_method)


def tropic(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Tropic divergent quantitative scheme"""
    return scheme('Tropic', bins, bin_method)


def earth(bins, bin_method=BinMethod.quantiles):
    """CARTOColors Earth divergent quantitative scheme"""
    return scheme('Earth', bins, bin_method)


def antique(bins, bin_method=BinMethod.category):
    """CARTOColors Antique qualitative scheme"""
    return scheme('Antique', bins, bin_method)


def bold(bins, bin_method=BinMethod.category):
    """CARTOColors Bold qualitative scheme"""
    return scheme('Bold', bins, bin_method)


def pastel(bins, bin_method=BinMethod.category):
    """CARTOColors Pastel qualitative scheme"""
    return scheme('Pastel', bins, bin_method)


def prism(bins, bin_method=BinMethod.category):
    """CARTOColors Prism qualitative scheme"""
    return scheme('Prism', bins, bin_method)


def safe(bins, bin_method=BinMethod.category):
    """CARTOColors Safe qualitative scheme"""
    return scheme('Safe', bins, bin_method)


def vivid(bins, bin_method=BinMethod.category):
    """CARTOColors Vivid qualitative scheme"""
    return scheme('Vivid', bins, bin_method)

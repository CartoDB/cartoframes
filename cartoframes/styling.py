"""Styling module that exposes CARTOColors schemes and others provided through
`palettable <https://github.com/jiffyclub/palettable/>`__. Read more about
CARTOColors in its `GitHub repository <https://github.com/Carto-color/>`__.

.. image:: https://cloud.githubusercontent.com/assets/1566273/21021002/fc9df60e-bd33-11e6-9438-d67951a7a9bf.png
    :width: 700px
    :alt: CARTOColors
"""  # noqa
import palettable

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


def get_scheme(scheme_info, scheme_attr):
    """"""
    try:
        # format is: palettable.<palette>.<type>
        # E.g., palettable.colorbrewer.diverging
        if scheme_info['provider'] in ('cartocolors', 'colorbrewer',
                                       'cmocean',):
            colors = getattr(
                getattr(
                    getattr(
                        palettable,
                        scheme_info['provider']),
                    scheme_info['type']),
                '{name}_{bins}{reverse}'.format(
                    name=scheme_info['name'],
                    bins=scheme_info['bins'],
                    reverse='_r' if scheme_info.get('reverse') else ''))
        # format is: palettable.<palette>
        # E.g., palettable.matplotlib
        elif scheme_info['provider'] in ('matplotlib', 'mycarta', 'tableau',
                                         'wesanderson',):
            colors = getattr(
                getattr(
                    palettable,
                    scheme_info['provider']),
                '{name}_{bins}{reverse}'.format(
                    name=scheme_info['name'],
                    bins=scheme_info['bins'],
                    reverse='_r' if scheme_info.get('reverse') else ''))
        elif scheme_info['provider'] == 'cubehelix':
            # TODO: provide more guidance on how to do this
            raise ValueError('Use `cubehelix` to generate a custom scheme and '
                             'pass its hex values to the scheme color keys '
                             'instead. Tip: accomplish this with `styling.'
                             'custom`')
    except AttributeError:
        raise AttributeError('A scheme called `{name}` with {bins} bins, of '
                             'type `{type}`, from palette `{provider}` does '
                             'not exist'.format(**scheme_info))
    return getattr(colors, scheme_attr)

# TODO: scheme_info should be updated to have `colors` key filled by being
#       given the proper provider's information


def get_scheme_cartocss(column, scheme_info):
    """Get TurboCARTO CartoCSS based on input parameters"""
    if 'colors' in scheme_info:
        color_scheme = '({})'.format(','.join(scheme_info['colors']))
    # turbocartocss providers
    elif scheme_info.get('provider') in ('colorbrewer', 'cartocolors',):
        color_scheme = '{provider}({name})'.format(
            # correct cartocolor(s) discrepancy in turbocartocss
            provider=(scheme_info['provider']
                      if scheme_info['provider'] != 'cartocolors'
                      else 'cartocolor'),
            name=scheme_info['name'])
    # TODO: remove this -- handle at a level higher up by providing colors
    elif scheme_info.get('provider') in ('cmocean', 'matplotlib', 'mycarta',
                                         'tableau', 'wesanderson',
                                         'cartocolors', ):
        colors = get_scheme(scheme_info, 'hex_colors')
        color_scheme = '({})'.format(','.join(colors))
    else:
        # fall back to defaults
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


def custom(colors, bins=None, bin_method=BinMethod.quantiles,
           provider=None, scheme_type=None, reverse=False):
    """Create a custom scheme.

    Args:
        colors (list of str): List of hex values for styling data
        bins (int, optional): Number of bins to style by. If not given, the
          number of colors will be used.
        bin_method (str, optional): Classification method. One of the values
          in :obj:`BinMethod`. Defaults to `quantiles`, which only works with
          quantitative data.
        provider (str): Origin of the color scheme. One of palettes listed on
          `palettable <http://jiffyclub.github.io/palettable/>`__ except
          cubeHelix.
        scheme_type (str): Type of scheme. One of `diverging` or `sequential`
          if 'cartocolors', 'colorbrewer', or 'cmocean' is the `provider`.
          Otherwise, this value is not used.
    """
    return {
        'colors': colors,
        'bins': bins if bins is not None else len(colors),
        'bin_method': bin_method,
        'provider': provider,
        'type': scheme_type,
        'reverse': reverse
    }

def scheme(name, bins, bin_method, provider, scheme_type, reverse):
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
        provider (str): Origin of the color scheme. One of palettes listed on
          `palettable <http://jiffyclub.github.io/palettable/>`__ except
          cubeHelix.
        scheme_type (str): Type of scheme. One of `diverging` or `sequential`
          if 'cartocolors', 'colorbrewer', or 'cmocean' is the `provider`.
          Otherwise, this value is not used.

    .. Warning::

       Input types are particularly sensitive in this function, and little
       feedback is given for errors. ``name`` and ``bin_method`` arguments
       are case-sensitive.

    """
    # TODO: fill in the additional arguments for ^^
    return {
        'name': name,
        'bins': bins,
        'bin_method': (bin_method if isinstance(bins, int) else ''),
        'provider': provider,
        'type': scheme_type,
        'reverse': reverse,
    }


# Get methods for CARTOColors schemes
def burg(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Burg quantitative scheme"""
    return scheme('Burg', bins, bin_method, 'cartocolors', 'sequential', reverse)


def burgYl(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors BurgYl quantitative scheme"""
    return scheme('BurgYl', bins, bin_method, 'cartocolors', 'sequential', reverse)


def redOr(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors RedOr quantitative scheme"""
    return scheme('RedOr', bins, bin_method, 'cartocolors', 'sequential', reverse)


def orYel(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors OrYel quantitative scheme"""
    return scheme('OrYel', bins, bin_method, 'cartocolors', 'sequential', reverse)


def peach(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Peach quantitative scheme"""
    return scheme('Peach', bins, bin_method, 'cartocolors', 'sequential', reverse)


def pinkYl(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors PinkYl quantitative scheme"""
    return scheme('PinkYl', bins, bin_method, 'cartocolors', 'sequential', reverse)


def mint(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Mint quantitative scheme"""
    return scheme('Mint', bins, bin_method, 'cartocolors', 'sequential', reverse)


def bluGrn(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors BluGrn quantitative scheme"""
    return scheme('BluGrn', bins, bin_method, 'cartocolors', 'sequential', reverse)


def darkMint(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors DarkMint quantitative scheme"""
    return scheme('DarkMint', bins, bin_method, 'cartocolors', 'sequential', reverse)


def emrld(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Emrld quantitative scheme"""
    return scheme('Emrld', bins, bin_method, 'cartocolors', 'sequential', reverse)


def bluYl(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors BluYl quantitative scheme"""
    return scheme('BluYl', bins, bin_method, 'cartocolors', 'sequential', reverse)


def teal(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Teal quantitative scheme"""
    return scheme('Teal', bins, bin_method, 'cartocolors', 'sequential', reverse)


def tealGrn(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors TealGrn quantitative scheme"""
    return scheme('TealGrn', bins, bin_method, 'cartocolors', 'sequential', reverse)


def purp(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Purp quantitative scheme"""
    return scheme('Purp', bins, bin_method, 'cartocolors', 'sequential', reverse)


def purpOr(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors PurpOr quantitative scheme"""
    return scheme('PurpOr', bins, bin_method, 'cartocolors', 'sequential', reverse)


def sunset(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Sunset quantitative scheme"""
    return scheme('Sunset', bins, bin_method, 'cartocolors', 'sequential', reverse)


def magenta(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Magenta quantitative scheme"""
    return scheme('Magenta', bins, bin_method, 'cartocolors', 'sequential', reverse)


def sunsetDark(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors SunsetDark quantitative scheme"""
    return scheme('SunsetDark', bins, bin_method, 'cartocolors', 'sequential', reverse)


def brwnYl(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors BrwnYl quantitative scheme"""
    return scheme('BrwnYl', bins, bin_method, 'cartocolors', 'sequential', reverse)


def armyRose(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors ArmyRose divergent quantitative scheme"""
    return scheme('ArmyRose', bins, bin_method, 'cartocolors', 'divergent', reverse)


def fall(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Fall divergent quantitative scheme"""
    return scheme('Fall', bins, bin_method, 'cartocolors', 'divergent', reverse)


def geyser(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Geyser divergent quantitative scheme"""
    return scheme('Geyser', bins, bin_method, 'cartocolors', 'divergent', reverse)


def temps(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Temps divergent quantitative scheme"""
    return scheme('Temps', bins, bin_method, 'cartocolors', 'divergent', reverse)


def tealRose(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors TealRose divergent quantitative scheme"""
    return scheme('TealRose', bins, bin_method, 'cartocolors', 'divergent', reverse)


def tropic(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Tropic divergent quantitative scheme"""
    return scheme('Tropic', bins, bin_method, 'cartocolors', 'divergent', reverse)


def earth(bins, bin_method=BinMethod.quantiles, reverse=False):
    """CartoColors Earth divergent quantitative scheme"""
    return scheme('Earth', bins, bin_method, 'cartocolors', 'divergent', reverse)


def antique(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Antique qualitative scheme"""
    return scheme('Antique', bins, bin_method, 'cartocolors', 'qualitative', reverse)


def bold(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Bold qualitative scheme"""
    return scheme('Bold', bins, bin_method, 'cartocolors', 'qualitative', reverse)


def pastel(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Pastel qualitative scheme"""
    return scheme('Pastel', bins, bin_method, 'cartocolors', 'qualitative', reverse)


def prism(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Prism qualitative scheme"""
    return scheme('Prism', bins, bin_method, 'cartocolors', 'qualitative', reverse)


def safe(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Safe qualitative scheme"""
    return scheme('Safe', bins, bin_method, 'cartocolors', 'qualitative', reverse)


def vivid(bins, bin_method=BinMethod.category, reverse=False):
    """CartoColors Vivid qualitative scheme"""
    return scheme('Vivid', bins, bin_method, 'cartocolors', 'qualitative', reverse)

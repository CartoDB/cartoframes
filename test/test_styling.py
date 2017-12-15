"""Unit tests for cartoframes.styling"""
import unittest
from cartoframes.styling import BinMethod, get_scheme_cartocss
from cartoframes import styling


class TestColorScheme(unittest.TestCase):
    """Tests for functions in key modules"""
    def setUp(self):
        # color schemes with all different names
        self.burg = styling.burg(bins=4)
        self.burgYl = styling.burgYl(bins=4)
        self.redOr = styling.redOr(bins=4)
        self.orYel = styling.orYel(bins=4)
        self.peach = styling.peach(bins=4)
        self.pinkYl = styling.pinkYl(bins=4)
        self.mint = styling.mint(bins=4)
        self.bluGrn = styling.bluGrn(bins=4)
        self.darkMint = styling.darkMint(bins=4)
        self.emrld = styling.emrld(bins=4)
        self.bluYl = styling.bluYl(bins=4)
        self.teal = styling.teal(bins=4)
        self.tealGrn = styling.tealGrn(bins=4)
        self.purp = styling.purp(bins=4)
        self.purpOr = styling.purpOr(bins=4)
        self.sunset = styling.sunset(bins=4)
        self.magenta = styling.magenta(bins=4)
        self.sunsetDark = styling.sunsetDark(bins=4)
        self.brwnYl = styling.brwnYl(bins=4)
        self.armyRose = styling.armyRose(bins=4)
        self.fall = styling.fall(bins=4)
        self.geyser = styling.geyser(bins=4)
        self.temps = styling.temps(bins=4)
        self.tealRose = styling.tealRose(bins=4)
        self.tropic = styling.tropic(bins=4)
        self.earth = styling.earth(bins=4)
        self.antique = styling.antique(bins=4)
        self.bold = styling.bold(bins=4)
        self.pastel = styling.pastel(bins=4)
        self.prism = styling.prism(bins=4)
        self.safe = styling.safe(bins=4)
        self.vivid = styling.vivid(bins=4)

    def test_styling_name(self):
        """styling.name with different sources"""

        # ensure correct color schemes are created
        # See more CARTO color schemes here: https://carto.com/carto-colors/
        self.assertEqual(self.burg['name'], 'Burg')
        self.assertEqual(self.burgYl['name'], 'BurgYl')
        self.assertEqual(self.redOr['name'], 'RedOr')
        self.assertEqual(self.orYel['name'], 'OrYel')
        self.assertEqual(self.peach['name'], 'Peach')
        self.assertEqual(self.pinkYl['name'], 'PinkYl')
        self.assertEqual(self.mint['name'], 'Mint')
        self.assertEqual(self.bluGrn['name'], 'BluGrn')
        self.assertEqual(self.darkMint['name'], 'DarkMint')
        self.assertEqual(self.emrld['name'], 'Emrld')
        self.assertEqual(self.bluYl['name'], 'BluYl')
        self.assertEqual(self.teal['name'], 'Teal')
        self.assertEqual(self.tealGrn['name'], 'TealGrn')
        self.assertEqual(self.purp['name'], 'Purp')
        self.assertEqual(self.purpOr['name'], 'PurpOr')
        self.assertEqual(self.sunset['name'], 'Sunset')
        self.assertEqual(self.magenta['name'], 'Magenta')
        self.assertEqual(self.sunsetDark['name'], 'SunsetDark')
        self.assertEqual(self.brwnYl['name'], 'BrwnYl')
        self.assertEqual(self.armyRose['name'], 'ArmyRose')
        self.assertEqual(self.fall['name'], 'Fall')
        self.assertEqual(self.geyser['name'], 'Geyser')
        self.assertEqual(self.temps['name'], 'Temps')
        self.assertEqual(self.tealRose['name'], 'TealRose')
        self.assertEqual(self.tropic['name'], 'Tropic')
        self.assertEqual(self.earth['name'], 'Earth')
        self.assertEqual(self.antique['name'], 'Antique')
        self.assertEqual(self.bold['name'], 'Bold')
        self.assertEqual(self.pastel['name'], 'Pastel')
        self.assertEqual(self.prism['name'], 'Prism')
        self.assertEqual(self.safe['name'], 'Safe')
        self.assertEqual(self.vivid['name'], 'Vivid')

        # basic properties
        self.assertEqual(self.prism['bins'], 4)
        self.assertEqual(self.temps['bin_method'], 'quantiles')

    def test_styling_values(self):
        """styling.BinMethod, etc."""
        # Raise AttributeError if invalid name is entered
        with self.assertRaises(AttributeError):
            styling.apple(bins=4, BinMethod=BinMethod.quantiles)

        # checks the number of bins for styling
        self.assertEqual(styling.vivid(bins=5)['bins'], 5)

        # check that bin method is as defined
        self.assertEqual(styling.vivid(bins=4,
                                       bin_method='category')['bin_method'],
                         'category')

    def test_get_scheme_cartocss(self):
        """styling.get_scheme_cartocss"""
        # test on category
        self.assertEqual(get_scheme_cartocss('acadia', self.vivid),
                         'ramp([acadia], cartocolor(Vivid), category(4), =)')
        # test on quantative
        self.assertEqual(get_scheme_cartocss('acadia', self.purp),
                         'ramp([acadia], cartocolor(Purp), quantiles(4), >)')
        # test on custom
        self.assertEqual(
            get_scheme_cartocss('acadia',
                                styling.custom(('#FFF', '#888', '#000'),
                                               bins=3,
                                               bin_method='equal')),
            'ramp([acadia], (#FFF,#888,#000), equal(3), >)')

        # test with non-int quantification
        self.assertEqual(
            get_scheme_cartocss('acadia',
                                styling.sunset([1, 2, 3])),
            'ramp([acadia], cartocolor(Sunset), (1,2,3), >=)')

    def test_scheme(self):
        """styling.scheme"""
        self.assertEqual(styling.scheme('acadia', 27, 'jenks'),
                         dict(name='acadia', bins=27, bin_method='jenks'))

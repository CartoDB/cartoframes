"""Unit tests for cartoframes.layers"""
import unittest
import json
from cartoframes.legends import Legend
from cartoframes import styling, Layer
import cartoframes
try:
    import matplotlib as mpl
except (ImportError, RuntimeError):
    mpl = None


class TestLegend(unittest.TestCase):
    """Tests for functions in keys module"""
    def setUp(self):
        creds = json.loads(open('test/secret.json').read())
        self.baseurl = 'https://{}.carto.com/'.format(creds['USERNAME'])
        self.apikey = creds['APIKEY']
        self.cc = cartoframes.CartoContext(base_url=self.baseurl,
                                           api_key=self.apikey)
        self.sql = self.cc.sql_client

    @unittest.skipIf(mpl is None,
                     'matplotlib not present, skipping test')
    def test_legend(self):
        """legends.Legend typical usage"""
        layer = Layer('tweets_obama', color={'column': 'friendscount',
                                             'scheme': styling.sunset(7)})
        leg = Legend(self.sql, layer)
        self.assertIsInstance(leg.draw_legend(),
                              mpl.colorbar.ColorbarBase)

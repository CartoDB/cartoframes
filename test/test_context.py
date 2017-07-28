"""Unit tests for cartoframes.layers"""
import unittest
import os
import cartoframes

class TestCartoContext(unittest.TestCase):
    """Tests for cartoframes.CartoContext"""
    APIKEY = os.environ["APIKEY"]
    USERNAME = os.environ["USERNAME"]
    BASEURL = 'https://{username}.carto.com/'.format(username=USERNAME)
    cc = cartoframes.CartoContext(base_url=BASEURL,
                                  api_key=APIKEY)
    df = cc.read('cb_2013_puma10_500k')

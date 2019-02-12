import unittest
from cartoframes.analysis import Table


class TestCredentials(unittest.TestCase):

    def test_table_repr(self):
        """analysis.Table.__repr__"""
        ans = 'Table(name=wadus_name)'
        self.assertEqual(str(Table('wadus_name')), ans)

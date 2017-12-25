# -*- coding: utf-8 -*-
"""Unit tests for cartoframes.utils"""
import unittest
from cartoframes.dataobs import get_countrytag


class TestUtils(unittest.TestCase):
    """Tests for functions in utils module"""
    def setUp(self):
        pass

    def test_get_countrytag(self):
        """dataobs.get_countrytag"""
        valid_regions = ('Australia', 'Brasil', 'EU', 'España', 'U.K.', )
        valid_answers = ['section/tags.{c}'.format(c=c)
                         for c in ('au', 'br', 'eu', 'spain', 'uk', )]
        invalid_regions = ('USofA', None, '', 'Jupiter', )

        for idx, r in enumerate(valid_regions):
            self.assertEqual(get_countrytag(r.lower()), valid_answers[idx])

        for r in invalid_regions:
            with self.assertRaises(ValueError):
                get_countrytag(r)

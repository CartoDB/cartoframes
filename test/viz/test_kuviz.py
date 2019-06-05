# -*- coding: utf-8 -*-

import unittest

from carto.exceptions import CartoException

from cartoframes.viz.kuviz import _validate_carto_kuviz
from mocks.kuviz_mock import KuvizMock, CartoKuvizMock
from mocks.context_mock import ContextMock


class TestKuviz(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.context = ContextMock(username=self.username, api_key=self.api_key)

        self.html = "<html><body><h1>Hi Kuviz yeee</h1></body></html>"

    def test_kuviz_create(self):
        name = 'test-name'
        kuviz = KuvizMock.create(context=self.context, html=self.html, name=name)
        self.assertIsNotNone(kuviz.vid)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, KuvizMock.PRIVACY_PUBLIC)

    def test_kuviz_create_with_password(self):
        name = 'test-name'
        kuviz = KuvizMock.create(context=self.context, html=self.html, name=name, password="1234")
        self.assertIsNotNone(kuviz.vid)
        self.assertIsNotNone(kuviz.url)
        self.assertEqual(kuviz.name, name)
        self.assertEqual(kuviz.privacy, KuvizMock.PRIVACY_PASSWORD)

    def test_kuviz_create_fails_without_all_fields(self):
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            KuvizMock.create(context=self.context, html=self.html, name=None)

    def test_kuviz_validation(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, password=None)
        result = _validate_carto_kuviz(carto_kuviz)
        self.assertTrue(result)

    def test_kuviz_validation_with_password(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, password="1234")
        result = _validate_carto_kuviz(carto_kuviz)
        self.assertTrue(result)

    def test_kuviz_validation_fails_without_id(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, id=None, password=None)
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            _validate_carto_kuviz(carto_kuviz)

    def test_kuviz_validation_fails_without_url(self):
        name = 'test-name'
        carto_kuviz = CartoKuvizMock(name=name, url=None, password=None)
        with self.assertRaises(CartoException, msg='Error creating Kuviz. Something goes wrong'):
            _validate_carto_kuviz(carto_kuviz)
